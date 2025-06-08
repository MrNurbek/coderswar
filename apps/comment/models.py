from django.db import models
from django.conf import settings
import random


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:  # Faqat yangi yaratilayotgan commentlar uchun
            self.likes = random.randint(1, 200)
            self.views = random.randint(1, 500)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.text[:30]}"
