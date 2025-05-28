from django.contrib.auth.models import AbstractUser
from django.db import models
import random

class CharacterClass(models.Model):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='character_classes/')

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    otm = models.CharField(max_length=100, verbose_name="Oliy ta'lim muassasasi")
    course = models.PositiveIntegerField(blank=True, null=True)
    group = models.CharField(max_length=20)
    direction = models.CharField(max_length=100)
    role = models.CharField(
        max_length=10,
        choices=[('talaba', 'Talaba'), ('oqituvchi', 'O‘qituvchi')],
        default='talaba'
    )
    rating = models.IntegerField(default=0)
    level = models.CharField(max_length=50, default='Rekrut')
    character = models.ForeignKey(CharacterClass, on_delete=models.SET_NULL, null=True ,blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"id-{self.id} - {self.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class ConfirmCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='confirm_code')
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.code}"