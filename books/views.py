from datetime import timedelta
import math

import boto3
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .models import Book, BookPage, BookComment, BookAnnotation, UserSubscription, BookShareUnlock
from reading.models import Rating, ReadingProgress


# =========================================================
# Helpers
# =========================================================
def _get_book_type(book: Book) -> str:
    if hasattr(book, "book_type") and getattr(book, "book_type"):
        return str(book.book_type)
    if hasattr(book, "type") and getattr(book, "type"):
        return str(book.type)
    if hasattr(book, "is_premium"):
        return "premium" if bool(getattr(book, "is_premium")) else "free"
    return "free"


def _created_at_display(dt):
    try:
        # Africa/Maputo já está no settings TIME_ZONE
        return dt.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def _user_label(user):
    return getattr(user, "email", "") or getattr(user, "username", "") or str(user)


def _has_active_subscription(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    now = timezone.now()
    return UserSubscription.objects.filter(user=user, expires_at__gt=now).exists()


def _has_share_unlock(user, book: Book) -> bool:
    if not user or not user.is_authenticated:
        return False
    return BookShareUnlock.objects.filter(user=user, book=book).exists()


def _allowed_until_page(book: Book, user) -> int:
    """
    Regras (B):
    - premium:
        - com plano ativo: total_pages
        - sem plano: 10% do total (mínimo 1)
    - free:
        - com share unlock: total_pages
        - sem unlock: 5% do total (mínimo 1)
    """
    total = int(getattr(book, "total_pages", 0) or 0)
    if total <= 0:
        # se não sabe total, deixa ler (ou ajusta depois)
        return 999999

    btype = _get_book_type(book)

    if btype == "premium":
        if _has_active_subscription(user):
            return total
        return max(1, math.ceil(total * 0.10))

    # free
    if _has_share_unlock(user, book):
        return total
    return max(1, math.ceil(total * 0.05))


def _payment_offers():
    # só dados para o frontend mostrar
    return [
        {"label": "1 semana", "price_mzn": 100, "days": 7},
        {"label": "1 mês", "price_mzn": 200, "days": 30},
        {"label": "3 meses", "price_mzn": 300, "days": 90},
        {"label": "6 meses", "price_mzn": 500, "days": 180},
        {"label": "1 ano", "price_mzn": 1000, "days": 365},
    ]


# =========================================================
# APIs
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
        try:
            created_at = b.created_at.isoformat() if getattr(b, "created_at", None) else None
        except Exception:
            created_at = None

        book_type = _get_book_type(b)

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
            "genre": str(getattr(b, "genre", "") or ""),
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
    # ✅ read SEMPRE exige login
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Auth required"}, status=401)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"detail": "Book not found"}, status=404)

    book_type = _get_book_type(book)
    total_pages = int(getattr(book, "total_pages", 0) or 0)

    allowed = _allowed_until_page(book, request.user)

    # ✅ bloqueio (premium -> pagar; free -> partilhar)
    if page_number > allowed:
        blocked_payload = {
            "blocked": True,
            "reason": "LIMIT_REACHED",
            "book_id": book.id,
            "title": str(getattr(book, "title", "") or ""),
            "book_type": book_type,
            "page_number": int(page_number),
            "total_pages": int(total_pages or 0),
            "allowed_until_page": int(allowed),
        }

        if book_type == "premium":
            blocked_payload["gate"] = "PAY"
            blocked_payload["offers"] = _payment_offers()
        else:
            blocked_payload["gate"] = "SHARE"
            blocked_payload["share_required"] = True

        return JsonResponse(blocked_payload, status=403)

    # buscar página
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
        "total_pages": int(total_pages or 0),
        "allowed_until_page": int(allowed),

        "page_image": page_url,
        "cover_url": cover_url,

        # extras úteis
        "share_unlocked": bool(_has_share_unlock(request.user, book)),
        "has_subscription": bool(_has_active_subscription(request.user)),
    })


# =========================================================
# Comentários
# =========================================================
@require_http_methods(["GET", "POST"])
def book_comments_api(request, book_id: int):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Auth required"}, status=401)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"detail": "Book not found"}, status=404)

    if request.method == "GET":
        page = int(request.GET.get("page") or 1)
        qs = BookComment.objects.filter(book=book, page_number=page).select_related("user").order_by("-created_at")[:200]
        out = []
        for c in qs:
            out.append({
                "id": c.id,
                "text": c.text,
                "user_label": _user_label(c.user),
                "created_at": c.created_at.isoformat(),
                "created_at_display": _created_at_display(c.created_at),
            })
        return JsonResponse(out, safe=False)

    # POST
    try:
        import json
        body = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        body = {}

    page_number = int(body.get("page_number") or 1)
    text = (body.get("text") or "").strip()

    if not text:
        return JsonResponse({"detail": "text is required"}, status=400)

    c = BookComment.objects.create(
        book=book,
        page_number=page_number,
        user=request.user,
        text=text
    )
    return JsonResponse({
        "id": c.id,
        "text": c.text,
        "user_label": _user_label(c.user),
        "created_at": c.created_at.isoformat(),
        "created_at_display": _created_at_display(c.created_at),
    }, status=201)


# =========================================================
# Anotações
# =========================================================
@require_http_methods(["GET", "POST"])
def book_annotations_api(request, book_id: int):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Auth required"}, status=401)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"detail": "Book not found"}, status=404)

    if request.method == "GET":
        page = int(request.GET.get("page") or 1)
        qs = BookAnnotation.objects.filter(book=book, page_number=page).select_related("user").order_by("-created_at")[:500]
        out = []
        for a in qs:
            out.append({
                "id": a.id,
                "text": a.text,
                "x": float(a.x),
                "y": float(a.y),
                "user_label": _user_label(a.user),
                "created_at": a.created_at.isoformat(),
                "created_at_display": _created_at_display(a.created_at),
                "mine": bool(a.user_id == request.user.id),
            })
        return JsonResponse(out, safe=False)

    # POST
    try:
        import json
        body = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        body = {}

    page_number = int(body.get("page_number") or 1)
    text = (body.get("text") or "").strip()
    x = body.get("x", None)
    y = body.get("y", None)

    if not text:
        return JsonResponse({"detail": "text is required"}, status=400)
    if x is None or y is None:
        return JsonResponse({"detail": "x and y are required"}, status=400)

    try:
        x = float(x)
        y = float(y)
    except Exception:
        return JsonResponse({"detail": "x and y must be numbers"}, status=400)

    # normaliza/clamp 0..1
    x = max(0.0, min(1.0, x))
    y = max(0.0, min(1.0, y))

    a = BookAnnotation.objects.create(
        book=book,
        page_number=page_number,
        user=request.user,
        text=text,
        x=x,
        y=y
    )
    return JsonResponse({
        "id": a.id,
        "text": a.text,
        "x": float(a.x),
        "y": float(a.y),
        "user_label": _user_label(a.user),
        "created_at": a.created_at.isoformat(),
        "created_at_display": _created_at_display(a.created_at),
        "mine": True,
    }, status=201)


@require_http_methods(["DELETE"])
def book_annotation_delete_api(request, annotation_id: int):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Auth required"}, status=401)

    try:
        a = BookAnnotation.objects.select_related("user").get(id=annotation_id)
    except BookAnnotation.DoesNotExist:
        return JsonResponse({"detail": "Not found"}, status=404)

    if a.user_id != request.user.id:
        return JsonResponse({"detail": "Forbidden"}, status=403)

    a.delete()
    return JsonResponse({"ok": True})


# =========================================================
# Unlock por share
# =========================================================
@require_POST
def book_unlock_share_api(request, book_id: int):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Auth required"}, status=401)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"detail": "Book not found"}, status=404)

    obj, created = BookShareUnlock.objects.get_or_create(user=request.user, book=book)
    return JsonResponse({
        "ok": True,
        "created": bool(created),
        "unlocked_at": obj.unlocked_at.isoformat(),
        "message": "Livro desbloqueado por partilha ✅"
    })