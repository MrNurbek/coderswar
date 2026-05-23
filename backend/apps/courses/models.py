from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class StudyLevel(models.TextChoices):
    BEGINNER     = 'beginner',     "Boshlang'ich"
    INTERMEDIATE = 'intermediate', "O'rta"
    ADVANCED     = 'advanced',     "Yuqori"


# ══════════════════════════════════════════════════════════════════════════════
# MODULE & TOPIC
# ══════════════════════════════════════════════════════════════════════════════

class Module(models.Model):
    number      = models.PositiveSmallIntegerField(unique=True)
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'Modul {self.number}: {self.title}'


class Topic(models.Model):
    """
    O'quv mavzusi — 45 ta mavzu, har biri 100 ball.

    Har bir mavzu 3 ta darajaga bo'linadi:
      Boshlang'ich (0–70%) → O'rta (70–90%) → Yuqori (90–100%)

    Har bir daraja uchun:
      • Video dars + Maruza matni  (TopicLevelContent)
      • 10 savollik test           (LevelTest)
      • 10 topshiriq + 1 loyiha   (Task — Side Quest)

    Ball taqsimoti (jami 100):
      MO=15  KO=35  FA=30  RE=20
    """

    class Difficulty(models.TextChoices):
        EASY   = 'easy',   'Oson'
        MEDIUM = 'medium', "O'rta"
        HARD   = 'hard',   'Qiyin'

    module      = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='topics')
    number      = models.PositiveSmallIntegerField()
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty  = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveSmallIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering        = ['number']
        unique_together = ('module', 'number')

    def __str__(self):
        return f'T{self.number}: {self.title}'

    # Ball mezonlari (4 mezon) — hujjat asosida
    MAX_MO = 15   # Motivatsion          — avtomatik (faollik, kontent, muddat, bonus)
    MAX_KO = 35   # Kognitiv             — avtomatik (testlar: B:10 + O:10 + Y:15)
    MAX_FA = 30   # Faoliyatli           — avtomatik:20 + o'qituvchi:10 (loyiha)
    MAX_RE = 20   # Refleksiv-baholovchi — avtomatik:10 (jurnal) + o'qituvchi:10 (peer)
    MAX_TOTAL = MAX_MO + MAX_KO + MAX_FA + MAX_RE  # 100


# ══════════════════════════════════════════════════════════════════════════════
# DARAJA KONTENTI  (o'qituvchi to'ldiradi)
# ══════════════════════════════════════════════════════════════════════════════

class TopicLevelContent(models.Model):
    """
    Har bir mavzu × daraja uchun video dars + maruza matni.
    O'qituvchi tomonidan to'ldiriladi.
    """
    topic        = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='level_contents')
    level        = models.CharField(max_length=15, choices=StudyLevel.choices)
    video_url    = models.URLField(blank=True, help_text='YouTube / Vimeo havolasi')
    lecture_text = models.TextField(blank=True, help_text='HTML yoki Markdown kontent')
    resources    = models.JSONField(
        default=list, blank=True,
        help_text='[{"title":"...","url":"..."}, ...]'
    )
    created_by   = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, related_name='created_level_contents'
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('topic', 'level')
        ordering        = ['topic__number', 'level']

    def __str__(self):
        return f'{self.topic} | {self.get_level_display()}'


# ══════════════════════════════════════════════════════════════════════════════
# DARAJA TESTI  (o'qituvchi to'ldiradi)
# ══════════════════════════════════════════════════════════════════════════════

class LevelTest(models.Model):
    """
    Daraja yakunidagi 10 savollik test.
    Har bir mavzuda 3 ta test (boshlang'ich / o'rta / yuqori).

    KO ball:   Boshlang'ich→5, O'rta→7, Yuqori→8  (jami max 20)
    AD ball:   Har darajadan o'tganda +5            (jami max 15)
    """
    KO_SCORE_MAP = {'beginner': 10, 'intermediate': 10, 'advanced': 15}  # jami 35

    topic      = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='level_tests')
    level      = models.CharField(max_length=15, choices=StudyLevel.choices)
    title      = models.CharField(max_length=200)
    pass_score = models.PositiveSmallIntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='O\'tish uchun minimal to\'g\'ri javoblar soni (10 dan)'
    )
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, related_name='created_tests'
    )
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('topic', 'level')
        ordering        = ['topic__number', 'level']

    def __str__(self):
        return f'{self.topic} | {self.get_level_display()} testi'


class LevelTestQuestion(models.Model):
    """Test savoli — 4 variant, 1 ta to'g'ri javob."""
    test           = models.ForeignKey(LevelTest, on_delete=models.CASCADE, related_name='questions')
    question       = models.TextField()
    options        = models.JSONField(help_text='["A) ...", "B) ...", "C) ...", "D) ..."]')
    correct_answer = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(3)],
        help_text='To\'g\'ri javob indeksi (0–3)'
    )
    explanation    = models.TextField(blank=True)
    order          = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.test} | #{self.order}: {self.question[:60]}'


class StudentLevelTestResult(models.Model):
    """Talabaning daraja testi natijasi (bir necha marta topshirish mumkin)."""
    student      = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='level_test_results')
    level_test   = models.ForeignKey(LevelTest, on_delete=models.CASCADE, related_name='results')
    score        = models.PositiveSmallIntegerField(default=0)
    passed       = models.BooleanField(default=False)
    answers      = models.JSONField(default=dict, help_text='{question_id: option_index}')
    attempt_no   = models.PositiveSmallIntegerField(default=1)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f'{self.student} | {self.level_test} | {self.score}/10 {"✓" if self.passed else "✗"}'


# ══════════════════════════════════════════════════════════════════════════════
# TALABA DARAJA JARAYONI
# ══════════════════════════════════════════════════════════════════════════════

class StudentLevelProgress(models.Model):
    """
    Talabaning mavzu × daraja bo'yicha video/matn holati.
    Video ko'rildi + matn o'qildi → AD ball beriladi.
    """
    student       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='level_progresses')
    topic         = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='student_level_progresses')
    level         = models.CharField(max_length=15, choices=StudyLevel.choices)
    video_watched = models.BooleanField(default=False)
    text_read     = models.BooleanField(default=False)
    ad_awarded    = models.BooleanField(default=False, help_text='AD ball berilganmi')
    completed_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'topic', 'level')

    def __str__(self):
        return f'{self.student} | {self.topic} | {self.level}'


# ══════════════════════════════════════════════════════════════════════════════
# TOPIC SCORE
# ══════════════════════════════════════════════════════════════════════════════

class TopicScore(models.Model):
    """
    Talabaning mavzu bo'yicha 4 ta mezon balli (jami 100).

      MO (15) — Avtomatik (faollik:5 + kontent:3 + muddat:3 + bonus:4)
      KO (35) — Avtomatik (testlar: B:10 + O:10 + Y:15)
      FA (30) — Avtomatik:20 (topshiriq+kontent) + O'qituvchi:10 (loyiha)
      RE (20) — Avtomatik:10 (jurnal) + O'qituvchi:10 (peer-review sifati)
    """

    student  = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='topic_scores')
    topic    = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='student_scores')
    level    = models.CharField(
        max_length=15, choices=StudyLevel.choices, default=StudyLevel.BEGINNER,
        help_text='Hozirgi o\'quv darajasi'
    )

    # Avtomatik ball'lar
    mo_score = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(15)])
    ko_score = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(35)])
    fa_score = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(20)],
                                                help_text='Avtomatik FA: topshiriq + kontent (max 20)')
    re_score = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(10)],
                                                help_text='Avtomatik RE: refleksiya jurnali (max 10)')

    # O'qituvchi tomonidan beriladigan ball'lar
    fa_project_score = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(10)],
        help_text='O\'qituvchi: loyiha baholash (max 10)'
    )
    re_peer_score = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(10)],
        help_text='O\'qituvchi: peer-review sifati (max 10)'
    )

    # Daraja test holati
    beginner_test_passed     = models.BooleanField(default=False)
    intermediate_test_passed = models.BooleanField(default=False)
    advanced_test_passed     = models.BooleanField(default=False)

    total_score   = models.PositiveSmallIntegerField(default=0, editable=False)
    attempt_count = models.PositiveSmallIntegerField(default=0)
    is_completed  = models.BooleanField(default=False)
    completed_at  = models.DateTimeField(null=True, blank=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'topic')
        ordering        = ['topic__number']

    def save(self, *args, **kwargs):
        self.total_score = (
            self.mo_score + self.ko_score
            + self.fa_score + self.fa_project_score
            + self.re_score + self.re_peer_score
        )
        pct = (self.total_score / Topic.MAX_TOTAL) * 100 if Topic.MAX_TOTAL else 0
        if pct >= 90:
            self.level = StudyLevel.ADVANCED
        elif pct >= 70:
            self.level = StudyLevel.INTERMEDIATE
        else:
            self.level = StudyLevel.BEGINNER

        # update_fields berilgan bo'lsa total_score va level ni ham qo'shish
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            uf = list(update_fields)
            for extra in ('total_score', 'level'):
                if extra not in uf:
                    uf.append(extra)
            kwargs['update_fields'] = uf

        super().save(*args, **kwargs)
        try:
            self.student.student_profile.recalculate()
        except Exception:
            pass
        # Badge tekshiruvi — topics_completed, perfect_score, level, module_completed
        try:
            from apps.gamification.services import check_and_award_badges
            check_and_award_badges(self.student)
        except Exception:
            pass

    def __str__(self):
        return f'{self.student} | {self.topic} | {self.total_score}/100'

    @property
    def completion_pct(self):
        return round((self.total_score / Topic.MAX_TOTAL) * 100)

    def award_level_test(self, level: str):
        """Daraja testidan o'tganda KO ballini berish."""
        ko_add = LevelTest.KO_SCORE_MAP.get(level, 0)
        updated = False
        if level == 'beginner' and not self.beginner_test_passed:
            self.ko_score = min(35, self.ko_score + ko_add)
            self.beginner_test_passed = True
            updated = True
        elif level == 'intermediate' and not self.intermediate_test_passed:
            self.ko_score = min(35, self.ko_score + ko_add)
            self.intermediate_test_passed = True
            updated = True
        elif level == 'advanced' and not self.advanced_test_passed:
            self.ko_score = min(35, self.ko_score + ko_add)
            self.advanced_test_passed = True
            updated = True
            if self.beginner_test_passed and self.intermediate_test_passed:
                from django.utils import timezone
                self.is_completed = True
                self.completed_at = timezone.now()
        if updated:
            self.save()

    def award_content_read(self, level: str):
        """Video + matn o'qilganda FA ball berish (bir marta, har daraja uchun +3)."""
        self.fa_score = min(20, self.fa_score + 3)   # 3 daraja × 3 = 9 (content portion)
        self.save(update_fields=['fa_score'])

    def award_task_score(self, level: str, category: str, points: int):
        """
        Topshiriq muvaffaqiyatli topshirilganda FA ball berish.
        Faqat exercise — loyiha (project) o'qituvchi tomonidan baholanadi.
        Avtomatik FA max = 20.
        """
        if category == 'exercise':
            self.fa_score = min(20, self.fa_score + points)
            self.save(update_fields=['fa_score'])


# ══════════════════════════════════════════════════════════════════════════════
# SIDE QUEST — TASK
# ══════════════════════════════════════════════════════════════════════════════

class Task(models.Model):
    """
    Side Quest vazifasi.

    Har bir mavzu × daraja uchun:
      10 ta Topshiriq (exercise) → FA ballini to'ldiradi
       1 ta Loyiha    (project)  → KR ballini to'ldiradi

    FA ball taqsimoti: B:8 + O:10 + Y:12 = 30
    KR ball taqsimoti: B:4 + O:5  + Y:6  = 15
    """

    class TaskCategory(models.TextChoices):
        EXERCISE = 'exercise', 'Topshiriq'
        PROJECT  = 'project',  'Loyiha'

    class TaskType(models.TextChoices):
        ALGORITHM    = 'algorithm',    'Algoritmik masala'
        DEBUG        = 'debug',        'Xatoni tuzatish'
        REFACTOR     = 'refactor',     'Qayta ishlash'
        MINI_PROJECT = 'mini_project', 'Mini-loyiha'

    # Daraja bo'yicha FA/KR maksimallari
    FA_LEVEL_MAX = {'beginner': 8, 'intermediate': 10, 'advanced': 12}
    KR_LEVEL_MAX = {'beginner': 4, 'intermediate': 5,  'advanced': 6}

    topic         = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tasks')
    level         = models.CharField(
        max_length=15, choices=StudyLevel.choices,
        help_text='Qaysi darajaga tegishli'
    )
    task_category = models.CharField(
        max_length=10, choices=TaskCategory.choices, default=TaskCategory.EXERCISE
    )
    task_type       = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.ALGORITHM)
    title           = models.CharField(max_length=200)
    description     = models.TextField()
    starter_code    = models.TextField(blank=True)
    expected_output = models.TextField(blank=True)
    test_cases      = models.JSONField(default=list)
    time_limit_ms   = models.PositiveIntegerField(default=2000)
    memory_limit_mb = models.PositiveIntegerField(default=256)
    max_score       = models.PositiveSmallIntegerField(
        default=1,
        help_text='Topshiriq uchun ball (exercise≈1, project≈5)'
    )
    order           = models.PositiveSmallIntegerField(default=0)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['level', 'task_category', 'order']
        indexes  = [models.Index(fields=['topic', 'level', 'task_category'])]

    def __str__(self):
        icon = '📋' if self.task_category == 'exercise' else '🏗️'
        return f'{icon} {self.topic} | {self.get_level_display()} | {self.title}'


# ══════════════════════════════════════════════════════════════════════════════
# SUBMISSION
# ══════════════════════════════════════════════════════════════════════════════

class Submission(models.Model):
    class Status(models.TextChoices):
        PENDING  = 'pending',  'Kutilmoqda'
        RUNNING  = 'running',  'Bajarilmoqda'
        PASSED   = 'passed',   "O'tdi ✓"
        FAILED   = 'failed',   'Xato ✗'
        ERROR    = 'error',    'Xatolik'
        TIMEOUT  = 'timeout',  'Vaqt tugadi'

    JUDGE0_CSHARP_ID = 51

    student       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='submissions')
    task          = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    code          = models.TextField()
    language      = models.CharField(max_length=20, default='csharp')
    status        = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    runtime_ms    = models.PositiveIntegerField(null=True, blank=True)
    memory_kb     = models.PositiveIntegerField(null=True, blank=True)
    judge0_token  = models.CharField(max_length=100, blank=True)
    test_results  = models.JSONField(default=list)
    score_awarded = models.PositiveSmallIntegerField(default=0)
    error_message = models.TextField(blank=True)
    submitted_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student} | {self.task} | {self.status}'


# ══════════════════════════════════════════════════════════════════════════════
# DIAGNOSTIK TEST
# ══════════════════════════════════════════════════════════════════════════════

class DiagnosticTest(models.Model):
    student      = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='diagnostic_test')
    score        = models.PositiveSmallIntegerField(default=0)
    level        = models.CharField(max_length=15, choices=StudyLevel.choices)
    answers      = models.JSONField(default=dict)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student} | {self.level} | {self.score}/20'


# ══════════════════════════════════════════════════════════════════════════════
# REFLEKSIYA JURNALI
# ══════════════════════════════════════════════════════════════════════════════

class ReflectionJournal(models.Model):
    student    = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reflections')
    topic      = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='reflections')
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'topic')
        ordering        = ['-created_at']

    def __str__(self):
        return f'{self.student} | {self.topic}'
