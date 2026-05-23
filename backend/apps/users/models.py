from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Platforma foydalanuvchisi — talaba, o'qituvchi yoki admin."""

    class Role(models.TextChoices):
        SUPERADMIN = 'superadmin', 'Superadmin'
        ADMIN      = 'admin',      'Admin'
        TEACHER    = 'teacher',    "O'qituvchi"
        STUDENT    = 'student',    'Talaba'

    role       = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone      = models.CharField(max_length=20, blank=True)
    bio        = models.TextField(blank=True)
    avatar     = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.get_full_name()} ({self.role})'

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER


class OTPCode(models.Model):
    """Email tasdiqlash uchun bir martalik kod."""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    code       = models.CharField(max_length=6)
    is_used    = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f'OTP {self.code} — {self.user.email}'


class Group(models.Model):
    """Talabalar guruhi."""
    name       = models.CharField(max_length=100)
    code       = models.CharField(max_length=20, unique=True)
    teacher    = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='teaching_groups',
        limit_choices_to={'role': 'teacher'}
    )
    year       = models.PositiveSmallIntegerField()
    faculty    = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    """Talabaning guruhga a'zoligi."""
    student   = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='group_memberships',
        limit_choices_to={'role': 'student'}
    )
    group     = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'group')

    def __str__(self):
        return f'{self.student} → {self.group}'


class StudentProfile(models.Model):
    """Talabaning o'yin profili — rating, daraja, karakter."""

    class Level(models.TextChoices):
        RECRUIT = 'recruit', 'Recruit'
        WARDEN  = 'warden',  'Warden'
        KNIGHT  = 'knight',  'Knight'
        HERO    = 'hero',    'Hero'
        LEGEND  = 'legend',  'Legend'
        LORD    = 'lord',    'Lord'
        DEITY   = 'deity',   'Deity'
        TITAN   = 'titan',   'Titan'

    class Character(models.TextChoices):
        WARRIOR     = 'warrior',     'Warrior ⚔️'
        RANGER      = 'ranger',      'Ranger 🏹'
        SORCERESS   = 'sorceress',   'Sorceress 🔮'
        KNIGHT      = 'knight',      'Knight 🛡️'
        LADY_KNIGHT = 'lady_knight', 'Lady Knight ⚜️'

    LEVEL_THRESHOLDS = {
        'recruit': (0, 300),
        'warden':  (301, 750),
        'knight':  (751, 1300),
        'hero':    (1301, 1900),
        'legend':  (1901, 2600),
        'lord':    (2601, 3350),
        'deity':   (3351, 4050),
        'titan':   (4051, 4500),
    }

    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    character      = models.CharField(max_length=20, choices=Character.choices, default=Character.WARRIOR)
    level          = models.CharField(max_length=20, choices=Level.choices, default=Level.RECRUIT)
    rating_score   = models.PositiveIntegerField(default=0)   # Σ topic scores
    academic_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # avg
    current_streak = models.PositiveIntegerField(default=0)
    max_streak     = models.PositiveIntegerField(default=0)
    last_active    = models.DateField(null=True, blank=True)
    duels_won      = models.PositiveIntegerField(default=0)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.get_full_name()} — {self.level} ({self.rating_score})'

    def update_level(self):
        for level, (lo, hi) in self.LEVEL_THRESHOLDS.items():
            if lo <= self.rating_score <= hi:
                self.level = level
                break
        self.save(update_fields=['level', 'updated_at'])

    def recalculate(self):
        from apps.courses.models import TopicScore
        scores = TopicScore.objects.filter(student=self.user, is_completed=True)
        total = sum(s.total_score for s in scores)
        count = scores.count()
        self.rating_score   = total
        self.academic_score = round(total / count, 2) if count else 0
        # Darajani hisoblash (save() chaqirmay)
        for level, (lo, hi) in self.LEVEL_THRESHOLDS.items():
            if lo <= self.rating_score <= hi:
                self.level = level
                break
        self.save(update_fields=['rating_score', 'academic_score', 'level', 'updated_at'])


class TeacherProfile(models.Model):
    """O'qituvchi profili."""
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=150, blank=True)
    title      = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.user.get_full_name()} — {self.department}'
