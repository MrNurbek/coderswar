from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from apps.userapp.models import User, ConfirmCode
import random
import string
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email', 'middle_name', 'first_name', 'last_name',
            'otm', 'course', 'group', 'direction', 'role',
            'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def generate_unique_username(self, base):
        """
        Bazaviy username'ga 4 ta random raqam qo‘shib, yagona `username` yaratadi.
        Kerak bo‘lsa, takrorlanmas bo‘lishi uchun bazada mavjudligini tekshiradi.
        """
        while True:
            username = f"{base}_{''.join(random.choices(string.digits, k=4))}"
            if not User.objects.filter(username=username).exists():
                return username

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])

        base_username = validated_data['email'].split('@')[0]
        validated_data['username'] = self.generate_unique_username(base_username)

        try:
            user = User.objects.create(**validated_data)
            ConfirmCode.objects.create(user=user)
            return user
        except IntegrityError as e:
            raise ValidationError({
                                      "detail": "Foydalanuvchini yaratishda xatolik yuz berdi. Iltimos, maʼlumotlarni tekshirib qayta urinib ko‘ring."})


class AcceptSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'otm', 'course', 'group', 'direction', 'role', 'rating',
            'level', 'character'
        ]
        read_only_fields = ['id', 'email', 'rating', 'level', 'character']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New password and confirm password do not match.")
        return data
