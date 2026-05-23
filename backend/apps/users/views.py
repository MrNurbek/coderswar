from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import OTPCode, Group, GroupMembership, StudentProfile
from .serializers import (
    MyTokenObtainPairSerializer, RegisterSerializer, OTPVerifySerializer,
    OTPVerifySerializer, PasswordChangeSerializer, UserDetailSerializer,
    StudentProfileSerializer, TeacherProfileSerializer,
    GroupSerializer, GroupMembershipSerializer, UserMiniSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer,
)
from .utils import send_otp_email, generate_otp, send_reset_password_email

User = get_user_model()


# ─── Auth ────────────────────────────────────────────────────────────────────

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """Yangi foydalanuvchi ro'yxatdan o'tishi."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        # OTP yuborish
        code = generate_otp()
        OTPCode.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )
        send_otp_email(user.email, code)

        # Birinchi login badge — faqat talabalar uchun
        if user.role == user.Role.STUDENT:
            try:
                from apps.gamification.services import check_and_award_badges
                check_and_award_badges(user)
            except Exception:
                pass


class OTPVerifyView(generics.GenericAPIView):
    """Email tasdiqlash."""
    serializer_class  = OTPVerifySerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=s.validated_data['email'])
        except User.DoesNotExist:
            return Response({'detail': 'Foydalanuvchi topilmadi.'}, status=404)

        otp = (
            OTPCode.objects
            .filter(user=user, code=s.validated_data['code'], is_used=False)
            .order_by('-created_at')
            .first()
        )
        if not otp or not otp.is_valid():
            return Response({'detail': 'Kod noto\'g\'ri yoki muddati o\'tgan.'}, status=400)

        otp.is_used = True
        otp.save(update_fields=['is_used'])
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        return Response({'detail': 'Email tasdiqlandi.'})


class ResendOTPView(generics.GenericAPIView):
    """OTP kodni qayta yuborish."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Topilmadi.'}, status=404)

        if user.is_verified:
            return Response({'detail': 'Allaqachon tasdiqlangan.'})

        code = generate_otp()
        OTPCode.objects.create(
            user=user, code=code,
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )
        send_otp_email(user.email, code)
        return Response({'detail': 'OTP qayta yuborildi.'})


# ─── Me / Profile ────────────────────────────────────────────────────────────

class MeView(generics.RetrieveUpdateAPIView):
    """Joriy foydalanuvchi profili."""
    serializer_class   = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        """User saqlandi — agar 'character' kelsa StudentProfile ga yozamiz."""
        user = serializer.save()
        char = self.request.data.get('character')
        if char:
            profile, _ = StudentProfile.objects.get_or_create(user=user)
            valid = [c[0] for c in StudentProfile.Character.choices]
            if char in valid:
                profile.character = char
                profile.save(update_fields=['character'])


class PasswordChangeView(generics.GenericAPIView):
    serializer_class   = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = request.user

        if not user.check_password(s.validated_data['old_password']):
            return Response({'detail': 'Eski parol noto\'g\'ri.'}, status=400)

        user.set_password(s.validated_data['new_password'])
        user.save(update_fields=['password'])
        return Response({'detail': 'Parol o\'zgartirildi.'})


# ─── Students public list ─────────────────────────────────────────────────────

class StudentListView(generics.ListAPIView):
    """Barcha talabalar ro'yxati (o'qituvchi/admin uchun)."""
    serializer_class   = UserMiniSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = User.objects.filter(role=User.Role.STUDENT).select_related('student_profile')
        group_id = self.request.query_params.get('group')
        if group_id:
            qs = qs.filter(group_memberships__group_id=group_id)
        return qs


class StudentProfileView(generics.RetrieveAPIView):
    """Bitta talabaning o'yin profili."""
    serializer_class   = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['user_id']
        return generics.get_object_or_404(StudentProfile, user_id=user_id)


# ─── Groups ──────────────────────────────────────────────────────────────────

class GroupViewSet(viewsets.ModelViewSet):
    serializer_class   = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (User.Role.SUPERADMIN, User.Role.ADMIN):
            return Group.objects.all()
        if user.role == User.Role.TEACHER:
            return Group.objects.filter(teacher=user)
        # Student faqat o'z guruhlarini ko'radi
        return Group.objects.filter(memberships__student=user)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        group = self.get_object()
        memberships = GroupMembership.objects.filter(group=group).select_related('student')
        s = GroupMembershipSerializer(memberships, many=True)
        return Response(s.data)

    @action(detail=True, methods=['post'], url_path='add-student')
    def add_student(self, request, pk=None):
        group = self.get_object()
        student_id = request.data.get('student_id')
        try:
            student = User.objects.get(id=student_id, role=User.Role.STUDENT)
        except User.DoesNotExist:
            return Response({'detail': 'Talaba topilmadi.'}, status=404)

        _, created = GroupMembership.objects.get_or_create(student=student, group=group)
        if not created:
            return Response({'detail': 'Allaqachon a\'zo.'}, status=400)
        return Response({'detail': 'Talaba qo\'shildi.'})

    @action(detail=True, methods=['delete'], url_path='remove-student')
    def remove_student(self, request, pk=None):
        group = self.get_object()
        student_id = request.data.get('student_id')
        deleted, _ = GroupMembership.objects.filter(
            student_id=student_id, group=group
        ).delete()
        if not deleted:
            return Response({'detail': 'A\'zolik topilmadi.'}, status=404)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Avatar Upload ────────────────────────────────────────────────────────────

class AvatarUploadView(generics.GenericAPIView):
    """
    Avatar yuklash: PATCH /api/auth/me/avatar/
    multipart/form-data: { avatar: <file> }
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def patch(self, request):
        user = request.user
        if 'avatar' not in request.FILES:
            return Response({'detail': 'avatar fayli topilmadi.'}, status=400)

        file = request.FILES['avatar']

        # Fayl hajmi tekshiruvi (max 2MB)
        if file.size > 2 * 1024 * 1024:
            return Response({'detail': 'Fayl hajmi 2MB dan oshmasligi kerak.'}, status=400)

        # Fayl turi tekshiruvi
        allowed = ('image/jpeg', 'image/png', 'image/webp', 'image/gif')
        if file.content_type not in allowed:
            return Response({'detail': 'Faqat JPG, PNG, WEBP yoki GIF ruxsat etilgan.'}, status=400)

        # Eski avatarni o'chirish
        if user.avatar:
            try:
                user.avatar.delete(save=False)
            except Exception:
                pass

        user.avatar = file
        user.save(update_fields=['avatar'])
        return Response({
            'detail': 'Avatar yangilandi.',
            'avatar': request.build_absolute_uri(user.avatar.url),
        })


# ─── Forgot / Reset Password ─────────────────────────────────────────────────

class ForgotPasswordView(generics.GenericAPIView):
    """
    Parolni tiklash bosqich 1: email yuborish.
    POST /api/auth/forgot-password/ { email }
    """
    serializer_class   = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        email = s.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Xavfsizlik uchun email mavjud bo'lmasa ham success qaytaramiz
            return Response({'detail': 'Agar email ro\'yxatdan o\'tgan bo\'lsa, kod yuborildi.'})

        code = generate_otp()
        OTPCode.objects.create(
            user       = user,
            code       = code,
            expires_at = timezone.now() + timezone.timedelta(minutes=15),
        )
        send_reset_password_email(user.email, code)
        return Response({'detail': 'Parol tiklash kodi emailingizga yuborildi.'})


class ResetPasswordView(generics.GenericAPIView):
    """
    Parolni tiklash bosqich 2: OTP + yangi parol.
    POST /api/auth/reset-password/ { email, code, new_password }
    """
    serializer_class   = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=s.validated_data['email'])
        except User.DoesNotExist:
            return Response({'detail': 'Foydalanuvchi topilmadi.'}, status=404)

        otp = (
            OTPCode.objects
            .filter(user=user, code=s.validated_data['code'], is_used=False)
            .order_by('-created_at')
            .first()
        )
        if not otp or not otp.is_valid():
            return Response({'detail': 'Kod noto\'g\'ri yoki muddati o\'tgan.'}, status=400)

        otp.is_used = True
        otp.save(update_fields=['is_used'])

        user.set_password(s.validated_data['new_password'])
        user.save(update_fields=['password'])
        return Response({'detail': 'Parol muvaffaqiyatli yangilandi.'})


# ─── Admin: User Block / Unblock ─────────────────────────────────────────────

class AdminUserBlockView(generics.GenericAPIView):
    """
    Foydalanuvchini bloklash / blokdan chiqarish (admin va superadmin uchun).
    POST /api/auth/users/<id>/block/
    POST /api/auth/users/<id>/unblock/
    """
    permission_classes = [permissions.IsAuthenticated]

    def _check_admin(self, request):
        if request.user.role not in (User.Role.ADMIN, User.Role.SUPERADMIN):
            return Response({'detail': 'Ruxsat yo\'q.'}, status=403)
        return None

    def post(self, request, user_id, action):
        err = self._check_admin(request)
        if err:
            return err

        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'Foydalanuvchi topilmadi.'}, status=404)

        # Superadmin ni bloklab bo'lmaydi
        if target.role == User.Role.SUPERADMIN:
            return Response({'detail': 'Superadminni bloklab bo\'lmaydi.'}, status=403)

        if action == 'block':
            target.is_active = False
            target.save(update_fields=['is_active'])
            return Response({'detail': f'{target.get_full_name()} bloklandi.'})
        elif action == 'unblock':
            target.is_active = True
            target.save(update_fields=['is_active'])
            return Response({'detail': f'{target.get_full_name()} blokdan chiqarildi.'})
        else:
            return Response({'detail': 'Noto\'g\'ri amal.'}, status=400)
