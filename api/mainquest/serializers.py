from rest_framework import serializers
from apps.mainquest.models import Topic, Plan, CodeExample, Assignment, AssignmentStatus


class CodeExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeExample
        fields = ['id', 'code','result']

class PlanShortSerializerForTopic(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'title']
        ref_name = 'PlanShortSerializerForTopic'

class PlanShortSerializerForAssignment(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'title']
        ref_name = 'PlanShortSerializerForAssignment'

class AssignmentListSerializer(serializers.ModelSerializer):
    plan_title = serializers.CharField(source='plan.title', read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'title', 'plan_title']


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'plan', 'task_description',  'expected_output', 'order']

class AssignmentDetailSerializer(serializers.ModelSerializer):
    plan = PlanShortSerializerForAssignment()

    class Meta:
        model = Assignment
        fields = ['id', 'title', 'plan', 'task_description', 'sample_input', 'expected_output', 'order', 'points']



class AssignmentStatusSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer()

    class Meta:
        model = AssignmentStatus
        fields = ['id', 'assignment', 'is_completed', 'earned_points', 'submitted_at']


class PlanSerializer(serializers.ModelSerializer):
    code_examples = CodeExampleSerializer(many=True, read_only=True)
    # assignments = AssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = ['id', 'title', 'text', 'code_examples']


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





class TopicSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'title']





class TopicWithPlansSerializer(serializers.ModelSerializer):
    plans = PlanShortSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'title', 'plans']





class PlanDetailSerializer(serializers.ModelSerializer):
    topic_video_url = serializers.URLField(source='topic.video_url', read_only=True)
    code_examples = CodeExampleSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = ['id', 'title', 'text', 'topic_video_url', 'code_examples']