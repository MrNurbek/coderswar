from rest_framework import serializers
from apps.mainquest.models import Topic, Plan, CodeExample, Assignment, AssignmentStatus


class CodeExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeExample
        fields = ['id', 'code']


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'plan', 'task_description',  'expected_output', 'order']



class AssignmentStatusSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer()

    class Meta:
        model = AssignmentStatus
        fields = ['id', 'assignment', 'is_completed', 'earned_points', 'submitted_at']


class PlanSerializer(serializers.ModelSerializer):
    code_examples = CodeExampleSerializer(many=True, read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = ['id', 'title', 'text', 'code_examples', 'assignments']


class PlanShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'title']


class TopicSerializer(serializers.ModelSerializer):
    plans = PlanSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'title', 'video_url', 'order', 'plans']


class TopicShortSerializer(serializers.ModelSerializer):
    plans = PlanShortSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'title', 'plans']
