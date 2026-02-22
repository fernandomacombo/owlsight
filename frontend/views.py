from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.contrib.auth import logout
from django.shortcuts import redirect

from books.models import Book


@ensure_csrf_cookie
@never_cache
def home(request):
    """
    ✅ Página pública real (sem fake).
    ✅ Puxa livros do banco.
    ✅ Featured + listagens reais.
    ✅ Filtro simples por GET (q, type, tag, sort).
    """
    q = (request.GET.get("q") or "").strip()
    book_type = (request.GET.get("type") or "").strip()      # free | premium
    tag = (request.GET.get("tag") or "").strip()
    sort = (request.GET.get("sort") or "recentes").strip()   # recentes | antigos | titulo

    qs = Book.objects.all().prefetch_related("tags")

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(author__icontains=q) |
            Q(genre__icontains=q) |
            Q(description__icontains=q)
        )

    if book_type in ("free", "premium"):
        qs = qs.filter(book_type=book_type)

    if tag:
        qs = qs.filter(tags__name__iexact=tag)

    if sort == "antigos":
        qs = qs.order_by("created_at")
    elif sort == "titulo":
        qs = qs.order_by("title")
    else:
        qs = qs.order_by("-created_at")

    featured = qs.first()
    most_recent = qs[:8]

    # “Mais lidos”: você ainda não tem campo de views/reads no Book.
    # Então por enquanto é uma lista separada mas real (mais recentes também).
    most_read = Book.objects.all().order_by("-created_at")[:8]

    ctx = {
        "featured": featured,
        "most_recent": most_recent,
        "most_read": most_read,
        "books": qs[:30],  # resultados principais
        "db_books_count": qs.count(),
        "db_mode": True,
    }
    return render(request, "frontend/index.html", ctx)


@ensure_csrf_cookie
@never_cache
def login_view(request):
    return render(request, "frontend/login.html")


@ensure_csrf_cookie
@never_cache
def register_view(request):
    return render(request, "frontend/register.html")


@ensure_csrf_cookie
@never_cache
def forgot_password_view(request):
    return render(request, "frontend/forgot_password.html")


@ensure_csrf_cookie
@never_cache
def reset_password_view(request):
    return render(request, "frontend/reset_password.html")


@never_cache
def read_view(request, book_id, page_number):
    # ✅ Busca real do livro no DB (se não existir dá 404)
    book = get_object_or_404(Book, id=book_id)
    return render(request, "frontend/read.html", {
        "book": book,
        "book_id": book.id,
        "page_number": page_number
    })


@never_cache
def favorites_view(request):
    return render(request, "frontend/favorites.html")


@ensure_csrf_cookie
@never_cache
def categories_view(request):
    return render(request, "frontend/categories.html")


@ensure_csrf_cookie
@never_cache
def account_view(request):
    return render(request, "frontend/account.html")


@ensure_csrf_cookie
@never_cache
def terms_view(request):
    return render(request, "frontend/terms.html")


@ensure_csrf_cookie
@never_cache
def privacy_view(request):
    return render(request, "frontend/privacy.html")

def logout_view(request):
    logout(request)
    return redirect("/")