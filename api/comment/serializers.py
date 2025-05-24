from rest_framework import serializers

from apps.comment.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    user_profile_image = serializers.ImageField(source='user.profile_image', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user_full_name', 'user_profile_image', 'text', 'created_at']
        read_only_fields = ['id', 'user_full_name', 'user_profile_image', 'created_at']


