
from rest_framework import serializers

from apps.sidequest.models import GearItem, UserGear


class GearItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GearItem
        fields = ['id', 'name', 'type', 'quality']


class UserGearSerializer(serializers.ModelSerializer):
    gear = GearItemSerializer()

    class Meta:
        model = UserGear
        fields = ['id', 'gear', 'obtained_at', 'is_equipped']


class CodeSubmitSerializer(serializers.Serializer):
    code = serializers.CharField()