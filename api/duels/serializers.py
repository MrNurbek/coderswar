from rest_framework import serializers

from api.mainquest.serializers import AssignmentSerializer
from apps.duels.models import DuelAssignment, Duel

class DuelAssignmentSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer()

    class Meta:
        model = DuelAssignment
        fields = ['assignment']

class DuelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Duel
        fields = []

class DuelJoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Duel
        fields = []


class DuelSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.full_name', read_only=True)
    opponent_name = serializers.CharField(source='opponent.full_name', read_only=True)

    class Meta:
        model = Duel
        fields = ['id', 'creator', 'creator_name', 'opponent', 'opponent_name', 'created_at', 'is_active', 'winner', 'started_at']

class DuelAssignmentsForUserSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer()

    class Meta:
        model = DuelAssignment
        fields = ['assignment']