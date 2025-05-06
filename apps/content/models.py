from django.db import models


class Content(models.Model):
    HOME_PAGE = 'home'
    PERSONAL_INFO = 'personal'

    CONTENT_CHOICES = [
        (HOME_PAGE, 'Home Page uchun'),
        (PERSONAL_INFO, 'Shaxsiy ma\'lumot uchun'),
    ]

    title = models.CharField(max_length=255)
    text = models.TextField()
    image = models.ImageField(upload_to='content_images/')
    content_type = models.CharField(max_length=10, choices=CONTENT_CHOICES, default=HOME_PAGE)

    def __str__(self):
        return self.title

