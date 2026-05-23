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
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('icon', models.CharField(max_length=10)),
                ('eq_type', models.CharField(choices=[('weapon', 'Qurol'), ('armor', 'Zirh'), ('ring', 'Uzuk'), ('boots', 'Etik')], max_length=10)),
                ('rarity', models.CharField(choices=[('common', 'Oddiy'), ('rare', 'Noyob'), ('epic', 'Epic'), ('legendary', 'Afsonaviy')], default='common', max_length=10)),
                ('attack_bonus', models.SmallIntegerField(default=0)),
                ('defense_bonus', models.SmallIntegerField(default=0)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['rarity', 'eq_type', 'name']},
        ),
        migrations.CreateModel(
            name='UserEquipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_equipped', models.BooleanField(default=False)),
                ('acquired_at', models.DateTimeField(auto_now_add=True)),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owners', to='gamification.equipment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-acquired_at']},
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('icon', models.CharField(default='🏅', max_length=10)),
                ('badge_type', models.CharField(choices=[('streak', 'Streak'), ('performance', 'Natija'), ('social', 'Ijtimoiy'), ('achievement', 'Yutuq'), ('special', 'Maxsus')], max_length=15)),
                ('condition', models.JSONField(default=dict)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('earned_at', models.DateTimeField(auto_now_add=True)),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='awarded_to', to='gamification.badge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='badges', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('user', 'badge')}},
        ),
        migrations.CreateModel(
            name='Duel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duel_type', models.CharField(choices=[('algorithmic', 'Algoritmik'), ('debug', 'Debug'), ('complex', 'Kompleks')], default='algorithmic', max_length=15)),
                ('status', models.CharField(choices=[('waiting', 'Kutilmoqda'), ('in_progress', 'Davom etmoqda'), ('completed', 'Yakunlandi'), ('cancelled', 'Bekor qilindi')], default='waiting', max_length=15)),
                ('challenger_code', models.TextField(blank=True)),
                ('opponent_code', models.TextField(blank=True)),
                ('challenger_score', models.PositiveSmallIntegerField(default=0)),
                ('opponent_score', models.PositiveSmallIntegerField(default=0)),
                ('rating_reward', models.PositiveSmallIntegerField(default=15)),
                ('room_id', models.CharField(max_length=50, unique=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('challenger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='duels_challenged', to=settings.AUTH_USER_MODEL)),
                ('opponent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='duels_opposed', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='courses.task')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='duels_won', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Clan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('tag', models.CharField(max_length=10, unique=True)),
                ('emblem', models.CharField(default='🏰', max_length=10)),
                ('description', models.TextField(blank=True)),
                ('rating_score', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('leader', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='led_clans', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-rating_score']},
        ),
        migrations.CreateModel(
            name='ClanMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('leader', 'Lider'), ('officer', 'Ofitser'), ('member', "A'zo")], default='member', max_length=10)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('clan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='gamification.clan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clan_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('clan', 'user')}},
        ),
        migrations.CreateModel(
            name='ClanWar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('war_type', models.CharField(choices=[('algorithmic', 'Algoritmik'), ('debug', 'Debug'), ('complex', 'Kompleks')], default='algorithmic', max_length=15)),
                ('status', models.CharField(choices=[('scheduled', 'Rejalashtirilgan'), ('in_progress', 'Davom etmoqda'), ('completed', 'Yakunlandi'), ('cancelled', 'Bekor qilindi')], default='scheduled', max_length=15)),
                ('clan1_score', models.PositiveSmallIntegerField(default=0)),
                ('clan2_score', models.PositiveSmallIntegerField(default=0)),
                ('scheduled_at', models.DateTimeField()),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('clan1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wars_as_clan1', to='gamification.clan')),
                ('clan2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wars_as_clan2', to='gamification.clan')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wars_won', to='gamification.clan')),
            ],
        ),
        migrations.CreateModel(
            name='ClanChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('clan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='gamification.clan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clan_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['created_at']},
        ),
    ]
