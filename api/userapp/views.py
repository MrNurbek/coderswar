import random

from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.userapp.models import ConfirmCode, User
from .serializers import RegisterSerializer, AcceptSerializer, LoginSerializer, UserProfileSerializer, \
    ChangePasswordSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            confirm_code = ConfirmCode.objects.get(user=user)
            confirm_code.code = code
            confirm_code.save()


            send_mail(
                subject='CodersWar: Email tasdiqlash kodi',
                message=f"Sizning tasdiqlash kodingiz: {code}",
                from_email='your_email@gmail.com',
                recipient_list=[user.email],
                fail_silently=False
            )

            return Response({'message': 'Foydalanuvchi yaratildi. Emailga tasdiqlash kodi yuborildi.'},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AcceptView(APIView):
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
                    return Response({'message': 'Email tasdiqlandi.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Kod xato.'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'Foydalanuvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
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

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
            user.password = make_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password changed successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)