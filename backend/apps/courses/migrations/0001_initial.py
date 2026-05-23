import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(unique=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['number']},
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField()),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('difficulty', models.CharField(choices=[('easy', 'Oson'), ('medium', "O'rta"), ('hard', 'Qiyin')], default='medium', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='courses.module')),
            ],
            options={'ordering': ['number'], 'unique_together': {('module', 'number')}},
        ),
        migrations.CreateModel(
            name='TopicLevelContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('beginner', "Boshlang'ich"), ('intermediate', "O'rta"), ('advanced', 'Yuqori')], max_length=15)),
                ('video_url', models.URLField(blank=True)),
                ('lecture_text', models.TextField(blank=True)),
                ('resources', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_level_contents', to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level_contents', to='courses.topic')),
            ],
            options={'ordering': ['topic__number', 'level'], 'unique_together': {('topic', 'level')}},
        ),
        migrations.CreateModel(
            name='LevelTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('beginner', "Boshlang'ich"), ('intermediate', "O'rta"), ('advanced', 'Yuqori')], max_length=15)),
                ('title', models.CharField(max_length=200)),
                ('pass_score', models.PositiveSmallIntegerField(default=7, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tests', to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level_tests', to='courses.topic')),
            ],
            options={'ordering': ['topic__number', 'level'], 'unique_together': {('topic', 'level')}},
        ),
        migrations.CreateModel(
            name='LevelTestQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('options', models.JSONField()),
                ('correct_answer', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(3)])),
                ('explanation', models.TextField(blank=True)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='courses.leveltest')),
            ],
            options={'ordering': ['order']},
        ),
        migrations.CreateModel(
            name='StudentLevelTestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField(default=0)),
                ('passed', models.BooleanField(default=False)),
                ('answers', models.JSONField(default=dict)),
                ('attempt_no', models.PositiveSmallIntegerField(default=1)),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('level_test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='courses.leveltest')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level_test_results', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-completed_at']},
        ),
        migrations.CreateModel(
            name='StudentLevelProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('beginner', "Boshlang'ich"), ('intermediate', "O'rta"), ('advanced', 'Yuqori')], max_length=15)),
                ('video_watched', models.BooleanField(default=False)),
                ('text_read', models.BooleanField(default=False)),
                ('ad_awarded', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level_progresses', to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_level_progresses', to='courses.topic')),
            ],
            options={'unique_together': {('student', 'topic', 'level')}},
        ),
        migrations.CreateModel(
            name='TopicScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('beginner', "Boshlang'ich"), ('intermediate', "O'rta"), ('advanced', 'Yuqori')], default='beginner', max_length=15)),
                ('mo_score', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10)])),
                ('ko_score', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(20)])),
                ('fa_score', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(30)])),
                ('ad_score', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(15)])),
                ('kr_score', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(15)])),
                ('re_score', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10)])),
                ('beginner_test_passed', models.BooleanField(default=False)),
                ('intermediate_test_passed', models.BooleanField(default=False)),
                ('advanced_test_passed', models.BooleanField(default=False)),
                ('total_score', models.PositiveSmallIntegerField(default=0, editable=False)),
                ('attempt_count', models.PositiveSmallIntegerField(default=0)),
                ('is_completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topic_scores', to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_scores', to='courses.topic')),
            ],
            options={'ordering': ['topic__number'], 'unique_together': {('student', 'topic')}},
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('beginner', "Boshlang'ich"), ('intermediate', "O'rta"), ('advanced', 'Yuqori')], max_length=15)),
                ('task_category', models.CharField(choices=[('exercise', 'Topshiriq'), ('project', 'Loyiha')], default='exercise', max_length=10)),
                ('task_type', models.CharField(choices=[('algorithm', 'Algoritmik masala'), ('debug', 'Xatoni tuzatish'), ('refactor', 'Qayta ishlash'), ('mini_project', 'Mini-loyiha')], default='algorithm', max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('starter_code', models.TextField(blank=True)),
                ('expected_output', models.TextField(blank=True)),
                ('test_cases', models.JSONField(default=list)),
                ('time_limit_ms', models.PositiveIntegerField(default=2000)),
                ('memory_limit_mb', models.PositiveIntegerField(default=256)),
                ('max_score', models.PositiveSmallIntegerField(default=1)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='courses.topic')),
            ],
            options={
                'ordering': ['level', 'task_category', 'order'],
                'indexes': [models.Index(fields=['topic', 'level', 'task_category'], name='courses_tas_topic_i_fae3f7_idx')],
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField()),
                ('language', models.CharField(default='csharp', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Kutilmoqda'), ('running', 'Bajarilmoqda'), ('passed', "O'tdi ✓"), ('failed', 'Xato ✗'), ('error', 'Xatolik'), ('timeout', 'Vaqt tugadi')], default='pending', max_length=10)),
                ('runtime_ms', models.PositiveIntegerField(blank=True, null=True)),
                ('memory_kb', models.PositiveIntegerField(blank=True, null=True)),
                ('judge0_token', models.CharField(blank=True, max_length=100)),
                ('test_results', models.JSONField(default=list)),
                ('score_awarded', models.PositiveSmallIntegerField(default=0)),
                ('error_message', models.TextField(blank=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='courses.task')),
            ],
            options={'ordering': ['-submitted_at']},
        ),
        migrations.CreateModel(
            name='DiagnosticTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField(default=0)),
                ('level', models.CharField(choices=[('beginner', "Boshlang'ich"), ('intermediate', "O'rta"), ('advanced', 'Yuqori')], max_length=15)),
                ('answers', models.JSONField(default=dict)),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='diagnostic_test', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReflectionJournal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reflections', to=settings.AUTH_USER_MODEL)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reflections', to='courses.topic')),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('student', 'topic')}},
        ),
    ]
