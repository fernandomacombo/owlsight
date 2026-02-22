import json
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg, Count

from .models import Favorite, Rating, ReadingProgress
from books.models import Book


@login_required
@require_GET
def progress_me(request):
    qs = (
        ReadingProgress.objects
        .filter(user=request.user)
        .select_related("book")
        .order_by("-updated_at")
    )

    data = []
    for p in qs:
        data.append({
            "book_id": p.book_id,
            "last_page": p.last_page,
            "progress_percent": p.progress_percent,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        })
    return JsonResponse(data, safe=False)


@login_required
@require_GET
def favorites_me(request):
    qs = Favorite.objects.filter(user=request.user).values_list("book_id", flat=True)
    data = [{"book_id": int(bid)} for bid in qs]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def favorites_toggle(request, book_id: int):
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Livro não existe."}, status=404)

    obj = Favorite.objects.filter(user=request.user, book=book).first()
    if obj:
        obj.delete()
        return JsonResponse({"ok": True, "favorited": False})
    Favorite.objects.create(user=request.user, book=book)
    return JsonResponse({"ok": True, "favorited": True})


@login_required
@require_POST
def rate_book(request, book_id: int):
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Livro não existe."}, status=404)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {}

    stars = int(payload.get("stars") or 0)
    if stars < 1 or stars > 5:
        return JsonResponse({"error": "Stars deve ser entre 1 e 5."}, status=400)

    Rating.objects.update_or_create(
        user=request.user,
        book=book,
        defaults={"stars": stars},
    )

    # devolve médias atualizadas (opcional, mas útil)
    agg = Rating.objects.filter(book=book).aggregate(
        avg=Avg("stars"),
        cnt=Count("id"),
    )
    return JsonResponse({
        "ok": True,
        "avg_rating": float(agg["avg"] or 0),
        "ratings_count": int(agg["cnt"] or 0),
    })