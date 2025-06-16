from django.conf import settings
from django.db import models

class ContactMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Murojaat: {self.full_name} ({self.email})"


class EmailSubmission(models.Model):
    email = models.EmailField(unique=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email