from django.db import models

from apps.userapp.models import User


# === Gear item ===
class GearItem(models.Model):
    GEAR_TYPES = [
        ('sword', 'Qilich'),
        ('spear', 'Nayza'),
        ('magic', 'Sehrli tayoq'),
        ('shield', 'Qalqon'),
        ('helmet', 'Dubulg`a'),
        ('armor', 'Zirh'),
        ('boots', 'Etik'),
        ('ring', 'Uzuk'),
    ]
    QUALITY = [
        ('basic', 'Oddiy'),
        ('medium', 'O‘rtacha'),
        ('rare', 'Qimmatbaho')
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=GEAR_TYPES)
    quality = models.CharField(max_length=10, choices=QUALITY)
    image = models.ImageField(
        upload_to="gear_images/",
        blank=True,
        null=True,
        verbose_name="Rasm")

    def __str__(self):
        return f"{self.name} ({self.get_quality_display()})"


class UserGear(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gear = models.ForeignKey(GearItem, on_delete=models.CASCADE)
    obtained_at = models.DateTimeField(auto_now_add=True)
    is_equipped = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.gear.name}"
