from datetime import timedelta

import boto3
from django.conf import settings
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.core.files.storage import default_storage

from .models import Book

# Se já criaste o model BookPage em books/models.py, importa aqui:
try:
    from .models import BookPage
except Exception:
    BookPage = None

from reading.models import Rating, ReadingProgress


# =========================================================
# Helpers (B2 S3 + URL assinada)
# =========================================================
def _s3_client():
    """
    Backblaze B2 S3-compatible client.
    Requer settings:
      AWS_S3_ENDPOINT_URL
      AWS_ACCESS_KEY_ID
      AWS_SECRET_ACCESS_KEY
      AWS_STORAGE_BUCKET_NAME
      (opcional) AWS_S3_REGION_NAME
    """
    endpoint = getattr(settings, "AWS_S3_ENDPOINT_URL", None)
    region = getattr(settings, "AWS_S3_REGION_NAME", None) or "us-east-1"

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
        region_name=region,
    )


def _presign_get(key: str, expires: int = 900) -> str:
    """
    Gera URL assinada curta para objeto privado no bucket.
    Guarda SEMPRE a key/path no DB, não a URL assinada.

    NOTA:
    - Mantive esta função caso você ainda use em algum lugar.
    - Mas para CAPA e PÁGINAS, vamos usar default_storage.url()
      (porque é o mesmo motor que já funciona na index).
    """
    if not key:
        return ""

    bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
    if not bucket:
        return ""

    s3 = _s3_client()
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires,
    )


def _filefield_key(filefield) -> str:
    """
    Para django-storages: normalmente o "key" é filefield.name
    (ex: 'media/pdfs/xxx.pdf' ou 'pdfs/xxx.pdf')
    """
    try:
        return getattr(filefield, "name", "") or ""
    except Exception:
        return ""


def _get_book_type(book: Book) -> str:
    """
    Resolve tipo: free/premium (compatível com vários nomes de campo).
    """
    if hasattr(book, "book_type") and getattr(book, "book_type"):
        return str(book.book_type)
    if hasattr(book, "type") and getattr(book, "type"):
        return str(book.type)
    if hasattr(book, "is_premium"):
        return "premium" if bool(getattr(book, "is_premium")) else "free"
    return "free"


# =========================================================
# APIs
# =========================================================
@require_GET
def books_list_api(request):
    """
    GET /api/books/
    Retorna livros + métricas:
      - avg_rating, ratings_count (Rating)
      - readers_count, active_readers (ReadingProgress)
    """
    now = timezone.now()
    active_window = now - timedelta(hours=24)

    # Agregações de ratings por livro
    rating_aggs = (
        Rating.objects.values("book_id")
        .annotate(avg=Avg("stars"), cnt=Count("id"))
    )
    rating_map = {r["book_id"]: r for r in rating_aggs}

    # Leitores totais (qualquer progresso)
    readers_aggs = (
        ReadingProgress.objects.values("book_id")
        .annotate(readers=Count("user_id", distinct=True))
    )
    readers_map = {r["book_id"]: r["readers"] for r in readers_aggs}

    # "A ler agora" (ativos nas últimas 24h)
    active_aggs = (
        ReadingProgress.objects.filter(updated_at__gte=active_window)
        .values("book_id")
        .annotate(active=Count("user_id", distinct=True))
    )
    active_map = {r["book_id"]: r["active"] for r in active_aggs}

    qs = Book.objects.all().order_by("-id")

    data = []
    for b in qs:
        # ✅ usa o storage (mesmo motor que já funciona no teu projeto)
        cover_url = ""
        try:
            if getattr(b, "cover", None) and b.cover.name:
                cover_url = default_storage.url(b.cover.name)
        except Exception:
            cover_url = ""

        created_at = None
        if hasattr(b, "created_at") and getattr(b, "created_at"):
            try:
                created_at = b.created_at.isoformat()
            except Exception:
                created_at = None

        book_type = _get_book_type(b)

        genre = ""
        if hasattr(b, "genre") and getattr(b, "genre"):
            genre = str(b.genre)
        elif hasattr(b, "category") and getattr(b, "category"):
            genre = str(b.category)

        r = rating_map.get(b.id, {})
        avg_rating = float(r.get("avg") or 0)
        ratings_count = int(r.get("cnt") or 0)

        readers_count = int(readers_map.get(b.id, 0) or 0)
        active_readers = int(active_map.get(b.id, 0) or 0)

        data.append({
            "id": b.id,
            "title": str(getattr(b, "title", "") or ""),
            "author": str(getattr(b, "author", "") or ""),
            "description": str(getattr(b, "description", "") or ""),
            "genre": genre,
            "book_type": book_type,
            "cover": cover_url,
            "created_at": created_at,

            "avg_rating": avg_rating,
            "ratings_count": ratings_count,
            "readers_count": readers_count,
            "active_readers": active_readers,
        })

    return JsonResponse(data, safe=False)


@require_GET
def books_list(request):
    qs = Book.objects.all().order_by("-id").values("id", "title", "book_type", "total_pages")[:50]
    return JsonResponse(list(qs), safe=False)


@require_GET
def read_page_api(request, book_id: int, page_number: int):
    """
    GET /api/read/<book_id>/<page_number>/
    Retorna:
      - page_image (URL assinada via default_storage.url)
      - cover_url  (URL assinada via default_storage.url) ✅ corrigido
    """
    # --- auth básica ---
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Auth required"}, status=401)

    # --- book ---
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"detail": "Book not found"}, status=404)

    # --- se ainda não tens BookPage, para aqui ---
    if BookPage is None:
        return JsonResponse({
            "detail": "BookPage model not available. Crie o model BookPage em books/models.py e rode migrations."
        }, status=500)

    # --- limite por plano (ajusta depois para o teu sistema real) ---
    book_type = _get_book_type(book)
    total_pages = int(getattr(book, "total_pages", 0) or 0)

    if book_type == "premium":
        allowed_until_page = 10
    else:
        allowed_until_page = total_pages if total_pages else 999999

    if page_number > allowed_until_page:
        return JsonResponse({
            "blocked": True,
            "reason": "LIMIT_REACHED",
            "allowed_until_page": allowed_until_page,
            "total_pages": total_pages,
        }, status=403)

    # --- se não existem páginas ainda, tenta gerar on-demand ---
    if not BookPage.objects.filter(book=book).exists():
        try:
            from .page_build import build_pages_if_missing
            build_pages_if_missing(book)
        except Exception:
            return JsonResponse({
                "detail": "Páginas não foram geradas ainda. Crie o gerador on-demand em books/page_build.py.",
                "hint": "Você precisa converter o PDF em imagens (BookPage) antes de conseguir ler."
            }, status=409)

    # --- buscar página ---
    try:
        page = BookPage.objects.get(book=book, page_number=page_number)
    except BookPage.DoesNotExist:
        return JsonResponse({
            "detail": "Page not found",
            "page_number": page_number,
            "total_pages": total_pages,
        }, status=404)

    # ✅ URL assinada curta para a página (via storage)
    page_url = default_storage.url(page.image_key)

    # ✅ CORREÇÃO: capa via storage também (não boto3 presign)
    cover_url = ""
    try:
        if getattr(book, "cover", None) and book.cover.name:
            cover_url = default_storage.url(book.cover.name)
    except Exception:
        cover_url = ""

    return JsonResponse({
        "blocked": False,
        "book_id": book.id,
        "title": str(getattr(book, "title", "") or ""),
        "book_type": book_type,
        "page_number": int(page.page_number),
        "total_pages": int(getattr(book, "total_pages", 0) or 0),
        "allowed_until_page": int(allowed_until_page),

        "page_image": page_url,
        "cover_url": cover_url,
    })