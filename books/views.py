from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Book

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import Book
from reading.models import Rating, ReadingProgress


@require_GET
def books_list_api(request):
    """
    GET /api/books/
    Retorna livros + métricas:
      - avg_rating, ratings_count (da tabela Rating)
      - readers_count, active_readers (da tabela ReadingProgress)
    """
    now = timezone.now()
    active_window = now - timedelta(hours=24)

    # agrega ratings por livro
    rating_aggs = (
        Rating.objects
        .values("book_id")
        .annotate(avg=Avg("stars"), cnt=Count("id"))
    )
    rating_map = {r["book_id"]: r for r in rating_aggs}

    # agrega leitores por livro (qualquer progresso)
    readers_aggs = (
        ReadingProgress.objects
        .values("book_id")
        .annotate(readers=Count("user_id", distinct=True))
    )
    readers_map = {r["book_id"]: r["readers"] for r in readers_aggs}

    # agrega "a ler agora" (ativos nas últimas 24h)
    active_aggs = (
        ReadingProgress.objects
        .filter(updated_at__gte=active_window)
        .values("book_id")
        .annotate(active=Count("user_id", distinct=True))
    )
    active_map = {r["book_id"]: r["active"] for r in active_aggs}

    qs = Book.objects.all().order_by("-id")

    data = []
    for b in qs:
        cover_url = ""
        try:
            if getattr(b, "cover", None):
                cover_url = b.cover.url or ""
        except Exception:
            cover_url = ""

        created_at = None
        if hasattr(b, "created_at") and getattr(b, "created_at"):
            try:
                created_at = b.created_at.isoformat()
            except Exception:
                created_at = None

        book_type = "free"
        if hasattr(b, "book_type") and getattr(b, "book_type"):
            book_type = str(b.book_type)
        elif hasattr(b, "type") and getattr(b, "type"):
            book_type = str(b.type)
        elif hasattr(b, "is_premium"):
            book_type = "premium" if bool(getattr(b, "is_premium")) else "free"

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