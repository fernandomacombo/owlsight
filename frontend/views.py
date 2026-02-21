from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache


@ensure_csrf_cookie
@never_cache
def home(request):
    """
    Página pública (rosto da Owlsight).
    Ainda sem DB: envia dados de exemplo (fallback) para index.html.
    Depois vamos ligar ao banco: featured, most_read, recent, recommended, all_books.
    """

    # ✅ Livro em destaque (fallback)
    featured = {
        "title": "O Voo da Coruja",
        "author": "Autor(a) Desconhecido(a)",
        "rating": "4.8",
        "readers": "12.4k",
        "category": "Ficção",
        "blurb": "Uma história intensa, cinematográfica e inteligente. Descubra por que tantos leitores estão a comentar este título.",
        "cover": "",     # quando tiveres imagem: URL ou caminho
        "read_url": "",  # quando tiveres rota real: /read/<id>/1/ (vamos montar depois)
        "avg_time": "1h 20m",
        "level": "Média",
    }

    # ✅ Listas (fallback)
    most_read = [
        {"id": 1, "title": "Livro Popular 1", "rating": "4.7", "readers": "9.3k"},
        {"id": 2, "title": "Livro Popular 2", "rating": "4.6", "readers": "7.8k"},
        {"id": 3, "title": "Livro Popular 3", "rating": "4.8", "readers": "11.2k"},
        {"id": 4, "title": "Livro Popular 4", "rating": "4.5", "readers": "6.9k"},
    ]

    recent = [
        {"id": 5, "title": "Novo Livro 1", "rating": "4.5", "readers": "2.1k"},
        {"id": 6, "title": "Novo Livro 2", "rating": "4.6", "readers": "1.7k"},
        {"id": 7, "title": "Novo Livro 3", "rating": "4.4", "readers": "1.2k"},
        {"id": 8, "title": "Novo Livro 4", "rating": "4.7", "readers": "3.4k"},
    ]

    # ✅ Só mostra recomendados se estiver autenticado
    recommended = []
    if request.user.is_authenticated:
        recommended = [
            {"id": 9, "title": "Sugestão 1", "match": 92, "rating": "4.8"},
            {"id": 10, "title": "Sugestão 2", "match": 88, "rating": "4.7"},
            {"id": 11, "title": "Sugestão 3", "match": 84, "rating": "4.6"},
            {"id": 12, "title": "Sugestão 4", "match": 80, "rating": "4.5"},
        ]

    # ✅ “Todos os livros” (fallback)
    all_books = [
        {"id": i, "title": f"Livro {i}", "rating": "4.6", "readers": "1.2k"} for i in range(1, 21)
    ]

    ctx = {
        "featured": featured,
        "most_read": most_read,
        "recent": recent,
        "recommended": recommended,
        "all_books": all_books,
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
    return render(request, "frontend/read.html", {"book_id": book_id, "page_number": page_number})


@never_cache
def favorites_view(request):
    return render(request, "frontend/favorites.html")


# ✅ Páginas que o index.html referencia (se ainda não existem, cria já)
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