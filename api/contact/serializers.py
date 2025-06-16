# contact/serializers.py
from rest_framework import serializers

from apps.contact.models import EmailSubmission


class ContactSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    message = serializers.CharField()


class EmailSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSubmission
        fields = ['id', 'email', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']
