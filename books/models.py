from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    class BookType(models.TextChoices):
        FREE = "free", "Free"
        PREMIUM = "premium", "Premium"

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=120, blank=True, default="")
    genre = models.CharField(max_length=80, blank=True, default="")
    release_year = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, default="")

    book_type = models.CharField(
        max_length=10,
        choices=BookType.choices,
        default=BookType.FREE
    )

    total_pages = models.PositiveIntegerField(null=True, blank=True)

    # upload_to NÃO leva "media/"
    cover = models.ImageField(upload_to="covers/", blank=True, null=True)
    pdf_file = models.FileField(upload_to="pdfs/", blank=True, null=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="books")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================================================
# PÁGINAS CONVERTIDAS (PDF → IMAGENS)
# =========================================================
class BookPage(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="pages"
    )

    page_number = models.PositiveIntegerField()
    image_key = models.CharField(max_length=500)  # guarda a KEY do B2 (não URL assinada)
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("book", "page_number")
        ordering = ["page_number"]

    def __str__(self):
        return f"{self.book.title} - Página {self.page_number}"