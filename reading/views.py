import math
from urllib.parse import urlsplit

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


def _pdf_url(book: Book) -> str:
    try:
        if book.pdf_file:
            return book.pdf_file.url
    except Exception:
        pass
    return ""


def _fallback_page_url_from_pdf(book: Book, page: int) -> str:
    """
    FALLBACK (se você ainda não tem BookPageImage no banco):
    tenta adivinhar a URL da imagem a partir do pdf_file.url.

    Exemplo de padrão esperado:
      PDF:   https://SEU_DOMINIO/.../pdfs/arquivo.pdf
      PAGES: https://SEU_DOMINIO/.../pages/<book_id>/0001.jpg

    Se o teu padrão for diferente, me diz como é o caminho e eu ajusto.
    """
    pdf = _pdf_url(book)
    if not pdf:
        return ""

    # pega base até "/pdfs/"
    # ex: https://x.com/media/pdfs/a.pdf -> base = https://x.com/media
    if "/pdfs/" not in pdf:
        return ""

    base = pdf.split("/pdfs/")[0]
    return f"{base}/pages/{book.id}/{page:04d}.jpg"


@login_required
@require_GET
def read_page(request, book_id: int, page: int):
    book = Book.objects.filter(id=book_id).first()
    if not book:
        return JsonResponse({"error": "Livro não encontrado."}, status=404)

    title = book.title
    book_type = (book.book_type or "free").lower()
    total_pages = int(book.total_pages or 0)
    cover_url = _cover_url(book)

    if total_pages <= 0:
        return JsonResponse({
            "error": "Este livro não tem total_pages definido.",
            "book": title,
            "book_type": book_type,
            "cover": cover_url,
        }, status=400)

    # ✅ limites: FREE 10% | PREMIUM 5%
    allowed_until = max(1, math.ceil(total_pages * (0.05 if book_type == "premium" else 0.10)))

    # ✅ bloqueio
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

    # ✅ 1) tenta buscar imagem no banco
    obj = BookPageImage.objects.filter(book_id=book_id, page_number=page).first()
    page_image_url = ""
    if obj and obj.image:
        try:
            page_image_url = obj.image.url
        except Exception:
            page_image_url = ""

    # ✅ 2) fallback: tenta montar link pelo pdf_file.url
    if not page_image_url:
        page_image_url = _fallback_page_url_from_pdf(book, page)

    if not page_image_url:
        return JsonResponse({
            "error": "Não encontrei a imagem da página. (Sem BookPageImage e fallback falhou)",
            "hint": "Crie BookPageImage para cada página, ou confirme o padrão pages/<book_id>/0001.jpg no Backblaze.",
            "book": title,
            "book_type": book_type,
            "total_pages": total_pages,
            "allowed_until_page": allowed_until,
            "cover": cover_url,
        }, status=404)

    # ✅ salva progresso (opcional)
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
    # por agora só confirma (depois podemos salvar num model para desbloquear 100% para o user)
    return JsonResponse({"ok": True, "message": "Partilha registrada!"})