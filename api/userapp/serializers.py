from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from apps.userapp.models import User, ConfirmCode


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

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        ConfirmCode.objects.create(user=user)  # Kod create qilingan
        return user

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