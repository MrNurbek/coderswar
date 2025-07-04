from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.mainquest.serializers import TopicSerializer
from apps.mainquest.models import UserProgress
from apps.userapp.models import User, ConfirmCode, CharacterClass
import random
import string
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

UserModel = get_user_model()


# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             'email', 'middle_name', 'first_name', 'last_name',
#             'otm', 'course', 'group', 'direction', 'role',
#             'password','profile_image'
#         ]
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }
#
#     def generate_unique_username(self, base):
#         """
#         Bazaviy username'ga 4 ta random raqam qo‘shib, yagona `username` yaratadi.
#         Kerak bo‘lsa, takrorlanmas bo‘lishi uchun bazada mavjudligini tekshiradi.
#         """
#         while True:
#             username = f"{base}_{''.join(random.choices(string.digits, k=4))}"
#             if not User.objects.filter(username=username).exists():
#                 return username
#
#     def create(self, validated_data):
#         validated_data['password'] = make_password(validated_data['password'])
#
#         base_username = validated_data['email'].split('@')[0]
#         validated_data['username'] = self.generate_unique_username(base_username)
#
#         try:
#             user = User.objects.create(**validated_data)
#             ConfirmCode.objects.create(user=user)
#             return user
#         except IntegrityError as e:
#             raise ValidationError({
#                                       "detail": "Foydalanuvchini yaratishda xatolik yuz berdi. Iltimos, maʼlumotlarni tekshirib qayta urinib ko‘ring."})



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    level = serializers.SerializerMethodField()
    level_image_url = serializers.SerializerMethodField()
    profile_image = serializers.ImageField(
        required=False, allow_null=True, write_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'middle_name', 'otm', 'course', 'group', 'direction',
            'role', 'character', 'profile_image', 'level', 'level_image_url'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'read_only': True},
        }

    def get_level(self, obj):
        return obj.level

    def get_level_image_url(self, obj):
        request = self.context.get('request')
        url = obj.level_image_url  # This is the property in User model
        if request is not None:
            return request.build_absolute_uri(url)
        return url

    def validate(self, data):
        # Qo‘shimcha validatsiyalarni bu yerga yozishingiz mumkin
        return data

    def generate_unique_username(self, base):
        while True:
            username = f"{base}_{''.join(random.choices(string.digits, k=4))}"
            if not User.objects.filter(username=username).exists():
                return username

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        base_username = validated_data['email'].split('@')[0]
        validated_data['username'] = self.generate_unique_username(base_username)
        user = User.objects.create(**validated_data)
        ConfirmCode.objects.create(user=user)
        return user


class RatingSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    level_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'rating', 'level', 'level_image_url']

    def get_level(self, obj):
        return obj.level

    def get_level_image_url(self, obj):
        request = self.context.get('request')
        url = obj.level_image_url
        if request is not None:
            return request.build_absolute_uri(url)
        return url



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
            'level', 'character', 'profile_image'
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


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Yangi parollar mos emas.")
        return data


class CharacterClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterClass
        fields = ['id', 'name', 'title', 'image']


class Register1Serializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = [
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'middle_name', 'otm', 'course', 'group', 'direction',
            'role', 'character', 'profile_image'
        ]

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            middle_name=validated_data.get('middle_name'),
            otm=validated_data['otm'],
            course=validated_data.get('course'),
            group=validated_data['group'],
            direction=validated_data['direction'],
            role=validated_data['role'],
            character=validated_data['character'],
            profile_image=validated_data.get('profile_image')
        )
        return user


class UserProgressSerializer(serializers.ModelSerializer):
    topic = TopicSerializer()

    class Meta:
        model = UserProgress
        fields = ['id', 'topic', 'is_completed', 'completed_at']
