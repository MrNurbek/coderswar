from rest_framework import generics, status, permissions
import random
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.mainquest.models import AssignmentStatus, UserProgress, Topic
from apps.sidequest.models import UserGear
from apps.userapp.models import ConfirmCode, User, CharacterClass, University, Course, Direction, Group
from .serializers import RegisterSerializer, AcceptSerializer, LoginSerializer, UserProfileSerializer, \
    ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, UserProgressSerializer, \
    CharacterClassSerializer, RatingSerializer
from ..mainquest.serializers import TopicSerializer
from ..sidequest.serializers import UserGearSerializer


# class RegisterView(APIView):
#     @swagger_auto_schema(request_body=RegisterSerializer, responses={201: 'Foydalanuvchi yaratildi. Emailga kod yuborildi.'})
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#
#             code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
#             confirm_code = ConfirmCode.objects.get(user=user)
#             confirm_code.code = code
#             confirm_code.save()
#
#             send_mail(
#                 subject='CodersWar: Email tasdiqlash kodi',
#                 message=f"Sizning tasdiqlash kodingiz: {code}",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 fail_silently=False
#             )
#
#             return Response({'message': 'Foydalanuvchi yaratildi. Emailga tasdiqlash kodi yuborildi.'}, status=status.HTTP_201_CREATED)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: 'Foydalanuvchi yaratildi. Emailga kod yuborildi.'}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # ConfirmCode orqali tasdiqlash kodi yangilanadi
            code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            confirm_code = user.confirm_code
            confirm_code.code = code
            confirm_code.save()

            send_mail(
                subject='CodersWar: Email tasdiqlash kodi',
                message=f"Sizning tasdiqlash kodingiz: {code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )

            return Response(
                {'message': 'Foydalanuvchi yaratildi. Emailga tasdiqlash kodi yuborildi.'},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChoicesAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Ro‘yxatdan o‘tishda kerakli tanlovlar (OTM, kurs, yo‘nalish, guruh) ro‘yxatini qaytaradi",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'universities': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                'courses': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
                'directions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                'groups': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
            }
        )}
    )
    def get(self, request):
        return Response({
            "universities": [choice[0] for choice in University.choices],
            "courses": [choice[0] for choice in Course.choices],
            "directions": [choice[0] for choice in Direction.choices],
            "groups": [choice[0] for choice in Group.choices],
        })


class AcceptView(APIView):
    @swagger_auto_schema(
        request_body=AcceptSerializer,
        responses={200: 'Email tasdiqlandi va token qaytarildi.'}
    )
    def post(self, request):
        serializer = AcceptSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                user = User.objects.get(email=email)
                if user.confirm_code.code == code:
                    user.is_active = True
                    user.save()
                    user.confirm_code.delete()

                    # Token yaratish
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'message': 'Email tasdiqlandi.',
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Kod xato.'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'Foydalanuvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer, responses={200: 'Login muvaffaqiyatli.'})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_active:
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
                else:
                    return Response({'error': 'Email tasdiqlanmagan.'}, status=status.HTTP_403_FORBIDDEN)
            return Response({'error': 'Email yoki parol xato.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Foydalanuvchi profili va statistikasi qaytariladi.",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(type=openapi.TYPE_OBJECT),  # yoki RegisterSerializer.as_schema()
                'gears': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                'assignments_completed': openapi.Schema(type=openapi.TYPE_INTEGER),
                'rating': openapi.Schema(type=openapi.TYPE_INTEGER),
                'topics_progress': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT))
            }
        )}
    )
    def get(self, request):
        user = request.user
        gears = UserGear.objects.filter(user=user)
        completed_assignments = AssignmentStatus.objects.filter(user=user, is_completed=True)
        progress = UserProgress.objects.filter(user=user)

        return Response({
            "user": RegisterSerializer(user).data,
            "gears": UserGearSerializer(gears, many=True).data,
            "assignments_completed": completed_assignments.count(),
            "rating": user.rating,
            "topics_progress": UserProgressSerializer(progress, many=True).data
        })


class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserProfileSerializer,
        responses={200: 'Profil muvaffaqiyatli yangilandi'}
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profil muvaffaqiyatli yangilandi",
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ChangePasswordSerializer, responses={200: 'Parol muvaffaqiyatli o‘zgartirildi.'})
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"error": "Oldingi parol noto‘g‘ri"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Parol muvaffaqiyatli o‘zgartirildi"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ForgotPasswordView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordSerializer, responses={200: 'Kod emailga yuborildi.'})
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
                confirm_code, created = ConfirmCode.objects.get_or_create(user=user)
                confirm_code.code = code
                confirm_code.save()

                send_mail(
                    subject="Parolni tiklash uchun kod",
                    message=f"Sizning parolni tiklash kodingiz: {code}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False
                )
                return Response({"message": "Kod emailga yuborildi."})
            except User.DoesNotExist:
                return Response({"error": "Bunday email topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ResetPasswordView(APIView):
    @swagger_auto_schema(request_body=ResetPasswordSerializer, responses={200: 'Parol yangilandi.'})
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']

            try:
                user = User.objects.get(email=email)
                if user.confirm_code.code != code:
                    return Response({"error": "Kod noto‘g‘ri."}, status=status.HTTP_400_BAD_REQUEST)
                user.set_password(new_password)
                user.save()
                user.confirm_code.delete()
                return Response({"message": "Parol yangilandi."})
            except User.DoesNotExist:
                return Response({"error": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CharacterListView(generics.ListAPIView):
    queryset = CharacterClass.objects.all()
    serializer_class = CharacterClassSerializer


class TopicListView(generics.ListAPIView):
    queryset = Topic.objects.all().order_by('order')
    serializer_class = TopicSerializer


class UserRatingListView(generics.ListAPIView):
    queryset = User.objects.filter(is_active=True).order_by('-rating')
    serializer_class = RatingSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Umumiy foydalanuvchilar reytingi bo‘yicha saralangan ro‘yxat.",
        responses={200: RatingSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)