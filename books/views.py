from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Book


@require_GET
def books_list_api(request):
    """
    GET /api/books/
    Retorna uma lista de livros no formato que o frontend (index.html) espera.
    """

    qs = Book.objects.all().order_by("-id")

    data = []
    for b in qs:
        # ✅ cover: tenta usar b.cover.url (ImageField/FileField)
        cover_url = ""
        try:
            if getattr(b, "cover", None):
                cover_url = b.cover.url or ""
        except Exception:
            cover_url = ""

        # ✅ created_at: se existir
        created_at = None
        if hasattr(b, "created_at") and getattr(b, "created_at"):
            try:
                created_at = b.created_at.isoformat()
            except Exception:
                created_at = None

        # ✅ book_type: tenta achar campo (book_type/type/is_premium)
        book_type = "free"
        if hasattr(b, "book_type") and getattr(b, "book_type"):
            book_type = str(b.book_type)
        elif hasattr(b, "type") and getattr(b, "type"):
            book_type = str(b.type)
        elif hasattr(b, "is_premium"):
            book_type = "premium" if bool(getattr(b, "is_premium")) else "free"

        # ✅ genre: tenta achar campo (genre/category)
        genre = ""
        if hasattr(b, "genre") and getattr(b, "genre"):
            genre = str(b.genre)
        elif hasattr(b, "category") and getattr(b, "category"):
            genre = str(b.category)

        # ✅ rating stats: se não existir, manda 0 (frontend aguenta)
        avg_rating = float(getattr(b, "avg_rating", 0) or 0)
        ratings_count = int(getattr(b, "ratings_count", 0) or 0)

        # ✅ readers/active: se não existir, manda 0
        readers_count = int(getattr(b, "readers_count", 0) or 0)
        active_readers = int(getattr(b, "active_readers", 0) or 0)

        data.append({
            "id": b.id,
            "title": str(getattr(b, "title", "") or ""),
            "author": str(getattr(b, "author", "") or ""),
            "description": str(getattr(b, "description", "") or ""),
            "genre": genre,
            "book_type": book_type,          # "free" | "premium"
            "cover": cover_url,              # URL completa do cover
            "created_at": created_at,         # ISO string ou null

            "avg_rating": avg_rating,
            "ratings_count": ratings_count,
            "readers_count": readers_count,
            "active_readers": active_readers,
        })

    return JsonResponse(data, safe=False)