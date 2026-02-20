from django.db import models

class UploadTest(models.Model):
    title = models.CharField(max_length=120)
    file = models.FileField(upload_to="uploads/tests/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title