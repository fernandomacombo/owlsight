from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reading_progress")
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name="progress")
    last_page = models.PositiveIntegerField(default=1)
    progress_percent = models.PositiveIntegerField(default=0)  # 0..100
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "book")

    def __str__(self):
        return f"{self.user} • {self.book} • {self.progress_percent}%"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book")

    def __str__(self):
        return f"{self.user} ❤️ {self.book}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name="ratings")
    stars = models.PositiveSmallIntegerField()  # 1..5
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "book")

    def __str__(self):
        return f"{self.user} ⭐ {self.stars} • {self.book}"