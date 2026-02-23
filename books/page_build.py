import io
from django.conf import settings
from django.db import transaction
import boto3
import pypdfium2 as pdfium

from .models import Book, BookPage


def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
        aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
        region_name=getattr(settings, "AWS_S3_REGION_NAME", None) or "us-east-1",
    )


def _bucket():
    return getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")


def _key_prefix() -> str:
    # se AWS_LOCATION="media" => prefix "media/"
    location = (getattr(settings, "AWS_LOCATION", "") or "").strip("/")
    return f"{location}/" if location else ""


def _render_pdf_pages(pdf_bytes: bytes, scale: float = 2.0, quality: int = 80):
    """
    Yields: (page_number, webp_bytes, width, height)
    """
    doc = pdfium.PdfDocument(pdf_bytes)

    for i in range(len(doc)):
        page = doc[i]
        bitmap = page.render(scale=scale)
        img = bitmap.to_pil()

        if img.mode != "RGB":
            img = img.convert("RGB")

        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=quality, method=6)
        w, h = img.size
        yield (i + 1, buf.getvalue(), w, h)


def build_pages_if_missing(book: Book) -> int:
    """
    Converte o PDF do livro em imagens (WEBP), envia para o B2,
    cria BookPage no DB. Só faz isso se ainda não existirem páginas.
    """
    existing = BookPage.objects.filter(book=book).count()
    if existing > 0:
        return existing

    if not book.pdf_file:
        raise ValueError("Este livro não tem pdf_file.")

    # lê bytes do PDF pelo storage do Django (B2)
    with book.pdf_file.open("rb") as f:
        pdf_bytes = f.read()

    s3 = _s3_client()
    bucket = _bucket()
    if not bucket:
        raise ValueError("AWS_STORAGE_BUCKET_NAME não definido.")

    prefix = _key_prefix()
    created = 0

    with transaction.atomic():
        for page_number, webp_bytes, w, h in _render_pdf_pages(pdf_bytes, scale=2.0, quality=80):
            key = f"{prefix}pages/{book.id}/{page_number:04d}.webp"

            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=webp_bytes,
                ContentType="image/webp",
                ACL="private",
            )

            BookPage.objects.create(
                book=book,
                page_number=page_number,
                image_key=key,
                width=w,
                height=h,
            )
            created += 1

        book.total_pages = created
        book.save(update_fields=["total_pages"])

    return created