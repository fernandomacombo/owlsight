from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache

# ✅ tenta importar o model real de livros (ajusta depois se necessário)
try:
    from books.models import Book  # modelo mais comum
except Exception:
    Book = None


@ensure_csrf_cookie
@never_cache
def home(request):
    """
    Página pública (rosto da Owlsight).
    ✅ Agora tenta buscar do DB.
    ✅ Se não houver DB/model/records, cai no fallback.
    """

    # -------------------------
    # FALLBACK (mantém teu layout vivo)
    # -------------------------
    featured_fallback = {
        "id": None,
        "title": "O Voo da Coruja",
        "author": "Autor(a) Desconhecido(a)",
        "rating": "4.8",
        "readers": "12.4k",
        "category": "Ficção",
        "blurb": "Uma história intensa, cinematográfica e inteligente. Descubra por que tantos leitores estão a comentar este título.",
        "cover": "",
        "read_url": "",
        "avg_time": "1h 20m",
        "level": "Média",
    }

    most_read_fallback = [
        {"id": 1, "title": "Livro Popular 1", "rating": "4.7", "readers": "9.3k"},
        {"id": 2, "title": "Livro Popular 2", "rating": "4.6", "readers": "7.8k"},
        {"id": 3, "title": "Livro Popular 3", "rating": "4.8", "readers": "11.2k"},
        {"id": 4, "title": "Livro Popular 4", "rating": "4.5", "readers": "6.9k"},
    ]

    recent_fallback = [
        {"id": 5, "title": "Novo Livro 1", "rating": "4.5", "readers": "2.1k"},
        {"id": 6, "title": "Novo Livro 2", "rating": "4.6", "readers": "1.7k"},
        {"id": 7, "title": "Novo Livro 3", "rating": "4.4", "readers": "1.2k"},
        {"id": 8, "title": "Novo Livro 4", "rating": "4.7", "readers": "3.4k"},
    ]

    all_books_fallback = [
        {"id": i, "title": f"Livro {i}", "rating": "4.6", "readers": "1.2k"} for i in range(1, 21)
    ]

    recommended_fallback = []
    if request.user.is_authenticated:
        recommended_fallback = [
            {"id": 9, "title": "Sugestão 1", "match": 92, "rating": "4.8"},
            {"id": 10, "title": "Sugestão 2", "match": 88, "rating": "4.7"},
            {"id": 11, "title": "Sugestão 3", "match": 84, "rating": "4.6"},
            {"id": 12, "title": "Sugestão 4", "match": 80, "rating": "4.5"},
        ]

    # -------------------------
    # DB (se existir)
    # -------------------------
    featured = featured_fallback
    most_read = most_read_fallback
    recent = recent_fallback
    all_books = all_books_fallback
    recommended = recommended_fallback
    db_books_count = 0
    db_mode = False

    if Book is not None:
        try:
            qs = Book.objects.all()
            db_books_count = qs.count()

            if db_books_count > 0:
                db_mode = True

                # ✅ featured: o mais recente (troca depois para "mais lido" / "em destaque")
                f = qs.order_by("-id").first()
                featured = _book_to_dict(f)

                # ✅ mais lidos: se tiver campo "reads" ou "views" usa; senão por id
                if hasattr(Book, "reads"):
                    most_qs = qs.order_by("-reads")[:8]
                elif hasattr(Book, "views"):
                    most_qs = qs.order_by("-views")[:8]
                else:
                    most_qs = qs.order_by("-id")[:8]

                most_read = [_book_to_dict(b) for b in most_qs]

                # ✅ recentes
                recent_qs = qs.order_by("-id")[:8]
                recent = [_book_to_dict(b) for b in recent_qs]

                # ✅ todos (primeiros 30)
                all_qs = qs.order_by("-id")[:30]
                all_books = [_book_to_dict(b) for b in all_qs]

                # ✅ recommended: por enquanto replica recentes (depois ligamos ao histórico)
                if request.user.is_authenticated:
                    recommended = [_book_to_dict(b) for b in recent_qs[:4]]

        except Exception:
            # se der qualquer erro (model diferente/fields diferentes), mantém fallback
            pass

    ctx = {
        "featured": featured,
        "most_read": most_read,
        "recent": recent,
        "recommended": recommended,
        "all_books": all_books,

        # ✅ debug para tu veres no template se está vindo do DB
        "db_books_count": db_books_count,
        "db_mode": db_mode,
    }
    return render(request, "frontend/index.html", ctx)


def _book_to_dict(b):
    """
    Converte Book -> dict sem rebentar mesmo que os campos tenham nomes diferentes.
    Ajustamos perfeito depois que tu mandares books/models.py
    """
    if not b:
        return {"id": None, "title": "Livro", "rating": "—", "readers": "—"}

    # tenta adivinhar campos comuns
    title = getattr(b, "title", None) or getattr(b, "name", None) or str(b)
    author = getattr(b, "author", "") or getattr(b, "writer", "") or ""
    category = getattr(b, "category", "") or getattr(b, "genre", "") or ""
    description = getattr(b, "description", "") or getattr(b, "blurb", "") or ""

    rating = getattr(b, "rating", None)
    rating = str(rating) if rating is not None else "4.6"

    readers = getattr(b, "readers", None)
    if readers is None:
        reads = getattr(b, "reads", None) or getattr(b, "views", None)
        readers = str(reads) if reads is not None else "—"

    # capa: tenta cover.url ou cover_url
    cover = ""
    if hasattr(b, "cover_url") and getattr(b, "cover_url"):
        cover = getattr(b, "cover_url")
    elif hasattr(b, "cover") and getattr(b, "cover"):
        try:
            cover = b.cover.url
        except Exception:
            cover = ""

    return {
        "id": b.id,
        "title": title,
        "author": author,
        "rating": rating,
        "readers": readers,
        "category": category,
        "blurb": description,
        "cover": cover,
        "read_url": f"/read/{b.id}/1/",
        "avg_time": getattr(b, "avg_time", "") or "—",
        "level": getattr(b, "level", "") or "—",
    }


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
    return render(request, "frontend/read.html", {"book_id": book_id, "page_number": page_number})


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