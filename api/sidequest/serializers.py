
from rest_framework import serializers

from apps.sidequest.models import GearItem, UserGear


class GearItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = GearItem
        fields = ['id', 'name', 'type', 'quality','image','image_url']

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            url = obj.image.url  # masalan: /media/gear_images/xxx.png
            return request.build_absolute_uri(url) if request else url
        return None


class UserGearSerializer(serializers.ModelSerializer):
    gear = GearItemSerializer()

    class Meta:
        model = UserGear
        fields = ['id', 'gear', 'obtained_at', 'is_equipped']


class CodeSubmitSerializer(serializers.Serializer):
    code = serializers.CharField()