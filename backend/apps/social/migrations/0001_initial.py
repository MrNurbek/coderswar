import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PeerReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ko_score', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(20)])),
                ('fa_score', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(30)])),
                ('ad_score', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(15)])),
                ('kr_score', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(15)])),
                ('re_score', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10)])),
                ('comment', models.TextField()),
                ('star_rating', models.PositiveSmallIntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='peer_reviews_given', to=settings.AUTH_USER_MODEL)),
                ('reviewee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='peer_reviews_received', to=settings.AUTH_USER_MODEL)),
                ('topic_score', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='peer_reviews', to='courses.topicscore')),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('reviewer', 'topic_score')}},
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('notif_type', models.CharField(choices=[('system', 'Tizim'), ('duel', 'Duel'), ('clan', 'Klan'), ('peer_review', 'Peer Review'), ('badge', 'Nishon'), ('topic', 'Mavzu'), ('teacher', "O'qituvchi")], default='system', max_length=15)),
                ('is_read', models.BooleanField(default=False)),
                ('link', models.CharField(blank=True, max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('login', 'Kirish'), ('topic', 'Mavzu'), ('submission', 'Kod topshirish'), ('duel', 'Duel'), ('review', 'Review')], max_length=15)),
                ('date', models.DateField()),
                ('detail', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
                'indexes': [models.Index(fields=['user', 'date'], name='social_acti_user_id_22d843_idx')],
            },
        ),
    ]
