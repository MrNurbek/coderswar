from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0003_peerreview_add_mo_score'),
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('msg_type', models.CharField(
                    choices=[
                        ('complaint',    'Shikoyat / Nosozlik'),
                        ('question',     'Savol (mavzu/topshiriq)'),
                        ('advisory',     'Tavsiya / Maslahat'),
                        ('announcement', "E'lon"),
                        ('general',      'Umumiy'),
                    ],
                    default='general',
                    max_length=20,
                )),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sender', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sent_messages',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('recipient', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='received_messages',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('related_topic', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='messages',
                    to='courses.topic',
                )),
                ('parent', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='replies',
                    to='social.message',
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
