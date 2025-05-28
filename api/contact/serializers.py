# contact/serializers.py
from rest_framework import serializers

class ContactSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    message = serializers.CharField()



