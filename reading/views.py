import math
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required

from books.models import Book
from .models import BookPageImage, ReadingProgress


def _cover_url(book: Book) -> str:
    try:
        if book.cover:
            return book.cover.url
    except Exception:
        pass
    return ""


@login_required
@require_GET
def read_page(request, book_id: int, page: int):
   from books.models import Book
from django.http import JsonResponse

# ...

book = Book.objects.filter(id=book_id).first()
if not book:
    # ✅ dica: mostra alguns livros existentes (pra você pegar o ID certo)
    sample = list(Book.objects.all().order_by("-id").values("id", "title")[:10])
    return JsonResponse({
        "error": "Livro não encontrado.",
        "hint": "Use /api/books/list/ para ver os IDs reais nesta base.",
        "available_sample": sample
    }, status=404)

        # ✅ opcional: salva total_pages no Book para não recalcular sempre
        book.total_pages = total_pages
        book.save(update_fields=["total_pages"])

    # ✅ 2) limites: FREE 10% | PREMIUM 5%
    allowed_until = max(1, math.ceil(total_pages * (0.05 if book_type == "premium" else 0.10)))

    # ✅ 3) bloqueio por limite
    if page > allowed_until:
        return JsonResponse({
            "blocked": True,
            "cta": "pay" if book_type == "premium" else "share",
            "message": (
                "Livro premium: faça o pagamento para desbloquear a leitura completa."
                if book_type == "premium"
                else "Livro grátis: partilhe o link para desbloquear a leitura completa."
            ),
            "book": title,
            "book_type": book_type,
            "total_pages": total_pages,
            "allowed_until_page": allowed_until,
            "cover": cover_url,
        }, status=403)

    # ✅ 4) buscar imagem da página
    obj = BookPageImage.objects.filter(book_id=book_id, page_number=page).first()
    if not obj or not obj.image:
        return JsonResponse({
            "error": "Página ainda não tem imagem cadastrada (BookPageImage).",
            "book": title,
            "book_type": book_type,
            "total_pages": total_pages,
            "allowed_until_page": allowed_until,
            "cover": cover_url,
        }, status=404)

    page_image_url = ""
    try:
        page_image_url = obj.image.url
    except Exception:
        page_image_url = ""

    if not page_image_url:
        return JsonResponse({
            "error": "Não foi possível gerar URL da imagem (storage).",
            "book": title,
            "book_type": book_type,
            "total_pages": total_pages,
            "allowed_until_page": allowed_until,
            "cover": cover_url,
        }, status=500)

    # ✅ 5) salva progresso
    percent = int(round((page / total_pages) * 100))
    ReadingProgress.objects.update_or_create(
        user=request.user,
        book=book,
        defaults={"last_page": page, "progress_percent": max(0, min(100, percent))}
    )

    return JsonResponse({
        "book": title,
        "book_type": book_type,
        "total_pages": total_pages,
        "allowed_until_page": allowed_until,
        "cover": cover_url,
        "page_image": page_image_url,
    })


@login_required
@require_POST
def unlock_share(request, book_id: int):
    return JsonResponse({"ok": True, "message": "Partilha registrada!"})