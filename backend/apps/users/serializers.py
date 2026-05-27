from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Group, GroupMembership, StudentProfile, TeacherProfile, OTPCode


# ─── Token ───────────────────────────────────────────────────────────────────

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT tokeniga qo'shimcha claim'lar qo'shish."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role']       = user.role
        token['full_name']  = user.get_full_name()
        token['is_verified'] = user.is_verified
        return token


# ─── Auth ────────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Parolni tasdiqlang')
    role      = serializers.ChoiceField(
        choices=[User.Role.STUDENT, User.Role.TEACHER],
        default=User.Role.STUDENT,
    )

    class Meta:
        model  = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Parollar mos kelmadi.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Profil yaratish
        if user.role == User.Role.STUDENT:
            StudentProfile.objects.create(user=user)
        elif user.role == User.Role.TEACHER:
            TeacherProfile.objects.create(user=user)
        return user


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code  = serializers.CharField(max_length=6)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email        = serializers.EmailField()
    code         = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])


# ─── User ────────────────────────────────────────────────────────────────────

class UserMiniSerializer(serializers.ModelSerializer):
    """Kichik ma'lumot — boshqa serializer'larda ishlatiladi."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ('id', 'username', 'full_name', 'avatar', 'role')

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class StudentProfileSerializer(serializers.ModelSerializer):
    user                   = UserMiniSerializer(read_only=True)
    level_pct              = serializers.SerializerMethodField()
    mo_avg                 = serializers.SerializerMethodField()
    ko_avg                 = serializers.SerializerMethodField()
    fa_avg                 = serializers.SerializerMethodField()
    re_avg                 = serializers.SerializerMethodField()
    completed_topics_count = serializers.SerializerMethodField()
    group_year             = serializers.SerializerMethodField()

    class Meta:
        model  = StudentProfile
        fields = (
            'user', 'character', 'level', 'rating_score', 'academic_score',
            'current_streak', 'max_streak', 'last_active', 'updated_at', 'level_pct',
            'mo_avg', 'ko_avg', 'fa_avg', 're_avg', 'completed_topics_count',
            'group_year',
        )
        read_only_fields = ('rating_score', 'academic_score', 'level', 'updated_at')

    def _score_stats(self, obj):
        """1 ta DB query bilan barcha mezon o'rtachalarini olish (instance-cache'd)."""
        if not hasattr(obj, '_mezon_stats'):
            from apps.courses.models import TopicScore
            from django.db.models import Avg, Count
            obj._mezon_stats = TopicScore.objects.filter(
                student=obj.user, is_completed=True
            ).aggregate(
                cnt       = Count('id'),
                mo        = Avg('mo_score'),
                ko        = Avg('ko_score'),
                fa_auto   = Avg('fa_score'),
                fa_proj   = Avg('fa_project_score'),
                re_auto   = Avg('re_score'),
                re_peer   = Avg('re_peer_score'),
            )
        return obj._mezon_stats

    def get_level_pct(self, obj):
        """Hozirgi darajadagi taraqqiyot foizi (0–100)."""
        lo, hi = StudentProfile.LEVEL_THRESHOLDS.get(obj.level, (0, 300))
        span = hi - lo
        if span == 0:
            return 100
        return min(100, round((obj.rating_score - lo) / span * 100))

    def get_mo_avg(self, obj):
        return round(float(self._score_stats(obj)['mo'] or 0), 1)

    def get_ko_avg(self, obj):
        return round(float(self._score_stats(obj)['ko'] or 0), 1)

    def get_fa_avg(self, obj):
        s = self._score_stats(obj)
        return round(float((s['fa_auto'] or 0) + (s['fa_proj'] or 0)), 1)

    def get_re_avg(self, obj):
        s = self._score_stats(obj)
        return round(float((s['re_auto'] or 0) + (s['re_peer'] or 0)), 1)

    def get_completed_topics_count(self, obj):
        return self._score_stats(obj)['cnt'] or 0

    def get_group_year(self, obj):
        """Talaba guruhining kursi (1, 2, 3...). Guruh topilmasa None."""
        membership = obj.user.group_memberships.select_related('group').first()
        return membership.group.year if membership else None


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model  = TeacherProfile
        fields = ('user', 'department', 'university', 'title')


class UserDetailSerializer(serializers.ModelSerializer):
    """To'liq profil (o'zini ko'rishi va tahrirlashi uchun)."""
    student_profile = StudentProfileSerializer(read_only=True)
    teacher_profile = TeacherProfileSerializer(read_only=True)
    full_name       = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'bio', 'avatar', 'is_verified', 'created_at', 'updated_at',
            'student_profile', 'teacher_profile',
        )
        read_only_fields = ('id', 'role', 'is_verified', 'created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


# ─── Group ───────────────────────────────────────────────────────────────────

class GroupSerializer(serializers.ModelSerializer):
    teacher      = UserMiniSerializer(read_only=True)
    teacher_id   = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.TEACHER),
        source='teacher', write_only=True, required=False, allow_null=True,
    )
    member_count = serializers.SerializerMethodField()

    class Meta:
        model  = Group
        fields = ('id', 'name', 'code', 'teacher', 'teacher_id', 'year', 'faculty',
                  'member_count', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_member_count(self, obj):
        return obj.memberships.count()


class GroupMembershipSerializer(serializers.ModelSerializer):
    student = UserMiniSerializer(read_only=True)
    group   = GroupSerializer(read_only=True)

    class Meta:
        model  = GroupMembership
        fields = ('id', 'student', 'group', 'joined_at')
        read_only_fields = ('id', 'joined_at')
