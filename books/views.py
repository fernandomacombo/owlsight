from datetime import timedelta

import boto3
from django.conf import settings
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.core.files.storage import default_storage

from .models import Book, BookPage, BookComment, BookAnnotation
from reading.models import Rating, ReadingProgress


# =========================================================
# Helpers (B2 S3 + URL assinada)
# =========================================================
def _s3_client():
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
    try:
        return getattr(filefield, "name", "") or ""
    except Exception:
        return ""


def _get_book_type(book: Book) -> str:
    if hasattr(book, "book_type") and getattr(book, "book_type"):
        return str(book.book_type)
    if hasattr(book, "type") and getattr(book, "type"):
        return str(book.type)
    if hasattr(book, "is_premium"):
        return "premium" if bool(getattr(book, "is_premium")) else "free"
    return "free"


# =========================================================
# APIs EXISTENTES
# =========================================================
@require_GET
def books_list_api(request):
    now = timezone.now()
    active_window = now - timedelta(hours=24)

    rating_aggs = (
        Rating.objects.values("book_id")
        .annotate(avg=Avg("stars"), cnt=Count("id"))
    )
    rating_map = {r["book_id"]: r for r in rating_aggs}

    readers_aggs = (
        ReadingProgress.objects.values("book_id")
        .annotate(readers=Count("user_id", distinct=True))
    )
    readers_map = {r["book_id"]: r["readers"] for r in readers_aggs}

    active_aggs = (
        ReadingProgress.objects.filter(updated_at__gte=active_window)
        .values("book_id")
        .annotate(active=Count("user_id", distinct=True))
    )
    active_map = {r["book_id"]: r["active"] for r in active_aggs}

    qs = Book.objects.all().order_by("-id")

    data = []
    for b in qs:
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
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Auth required"}, status=401)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"detail": "Book not found"}, status=404)

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

    if not BookPage.objects.filter(book=book).exists():
        try:
            from .page_build import build_pages_if_missing
            build_pages_if_missing(book)
        except Exception:
            return JsonResponse({
                "detail": "Páginas não foram geradas ainda. Crie o gerador on-demand em books/page_build.py.",
                "hint": "Você precisa converter o PDF em imagens (BookPage) antes de conseguir ler."
            }, status=409)

    try:
        page = BookPage.objects.get(book=book, page_number=page_number)
    except BookPage.DoesNotExist:
        return JsonResponse({
            "detail": "Page not found",
            "page_number": page_number,
            "total_pages": total_pages,
        }, status=404)

    page_url = default_storage.url(page.image_key)

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


# =========================================================
# ✅ DRF: COMMENTS + ANNOTATIONS (REAL)
# =========================================================
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import BookCommentSerializer, BookAnnotationSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def book_comments_api(request, book_id: int):
    if not Book.objects.filter(id=book_id).exists():
        return Response({"detail": "Livro não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        page = request.query_params.get("page")
        qs = BookComment.objects.filter(book_id=book_id)
        if page is not None:
            try:
                qs = qs.filter(page_number=int(page))
            except ValueError:
                return Response({"detail": "page inválido."}, status=400)

        qs = qs.order_by("-created_at")
        return Response(BookCommentSerializer(qs, many=True).data)

    # POST
    page_number = request.data.get("page_number")
    text = (request.data.get("text") or "").strip()

    if not page_number or not str(page_number).isdigit():
        return Response({"detail": "page_number inválido."}, status=400)
    if not text:
        return Response({"detail": "text é obrigatório."}, status=400)

    obj = BookComment.objects.create(
        book_id=book_id,
        page_number=int(page_number),
        user=request.user,
        text=text,
    )
    return Response(BookCommentSerializer(obj).data, status=201)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def book_annotations_api(request, book_id: int):
    if not Book.objects.filter(id=book_id).exists():
        return Response({"detail": "Livro não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        page = request.query_params.get("page")
        qs = BookAnnotation.objects.filter(book_id=book_id)
        if page is not None:
            try:
                qs = qs.filter(page_number=int(page))
            except ValueError:
                return Response({"detail": "page inválido."}, status=400)

        qs = qs.order_by("-created_at")
        return Response(BookAnnotationSerializer(qs, many=True).data)

    # POST
    page_number = request.data.get("page_number")
    text = (request.data.get("text") or "").strip()
    x = request.data.get("x")
    y = request.data.get("y")

    if not page_number or not str(page_number).isdigit():
        return Response({"detail": "page_number inválido."}, status=400)
    if not text:
        return Response({"detail": "text é obrigatório."}, status=400)

    try:
        x = float(x)
        y = float(y)
    except (TypeError, ValueError):
        return Response({"detail": "x/y inválidos."}, status=400)

    if not (0 <= x <= 1 and 0 <= y <= 1):
        return Response({"detail": "x/y devem estar entre 0 e 1."}, status=400)

    obj = BookAnnotation.objects.create(
        book_id=book_id,
        page_number=int(page_number),
        user=request.user,
        text=text,
        x=x,
        y=y,
    )
    return Response(BookAnnotationSerializer(obj).data, status=201)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def book_annotation_delete_api(request, annotation_id: int):
    obj = BookAnnotation.objects.filter(id=annotation_id).first()
    if not obj:
        return Response({"detail": "Não encontrado."}, status=404)

    if obj.user_id != request.user.id:
        return Response({"detail": "Sem permissão."}, status=403)

    obj.delete()
    return Response(status=204)