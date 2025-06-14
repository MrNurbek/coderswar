from django.contrib.auth.models import AbstractUser
from django.db import models
import random

class CharacterClass(models.Model):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='character_classes/')

    def __str__(self):
        return self.name


class University(models.TextChoices):
    TERDU = 'TerDU', 'TerDU'
    GULDU = 'GulDU', 'GulDU'
    FARDU = 'FarDU', 'FarDU'

class Course(models.IntegerChoices):
    FIRST = 1, '1'
    SECOND = 2, '2'
    THIRD = 3, '3'
    FOURTH = 4, '4'

class Direction(models.TextChoices):
    AMALIY_MATEMATIKA = 'Amaliy matematika', 'Amaliy matematika'

class Group(models.TextChoices):
    G101 = '101', '101'
    G102 = '102', '102'
    G103 = '103', '103'
    G201 = '201', '201'
    G202 = '202', '202'
    G203 = '203', '203'
    G301 = '301', '301'
    G302 = '302', '302'
    G303 = '303', '303'
    G401 = '401', '401'
    G402 = '402', '402'
    G403 = '403', '403'

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    otm = models.CharField(max_length=10, choices=University.choices)
    course = models.IntegerField(choices=Course.choices , null=True, blank=True)
    group = models.CharField(max_length=10, choices=Group.choices)
    direction = models.CharField(max_length=100, choices=Direction.choices)
    role = models.CharField(
        max_length=10,
        choices=[('talaba', 'Talaba'), ('oqituvchi', 'O‘qituvchi')],
        default='talaba'
    )
    rating = models.IntegerField(default=0)
    character = models.ForeignKey(CharacterClass, on_delete=models.SET_NULL, null=True ,blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"id-{self.id} - {self.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def level(self):
        if self.rating < 1500:
            return 'Recruit'
        elif self.rating < 3000:
            return 'Warden'
        elif self.rating < 4500:
            return 'Knight'
        elif self.rating < 6000:
            return 'Hero'
        elif self.rating < 7500:
            return 'Legend'
        elif self.rating < 8500:
            return 'Lord'
        elif self.rating < 9500:
            return 'Deity'
        else:
            return 'Titan'

    @property
    def level_image_url(self):
        level_name = self.level.lower()  # e.g. 'recruit'
        return f"/static/images/levels/{level_name}.png"



class ConfirmCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='confirm_code')
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.code}"