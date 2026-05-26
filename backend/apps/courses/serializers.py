from rest_framework import serializers
from .models import (
    Module, Topic, TopicLevelContent,
    LevelTest, LevelTestQuestion, StudentLevelTestResult,
    StudentLevelProgress, TopicScore,
    Task, Submission, DiagnosticTest, ReflectionJournal,
)


# ─── Module ──────────────────────────────────────────────────────────────────

class ModuleSerializer(serializers.ModelSerializer):
    topic_count = serializers.SerializerMethodField()

    class Meta:
        model  = Module
        fields = ('id', 'number', 'title', 'description', 'is_active', 'topic_count')

    def get_topic_count(self, obj):
        return obj.topics.filter(is_active=True).count()


# ─── TopicLevelContent ───────────────────────────────────────────────────────

class TopicLevelContentSerializer(serializers.ModelSerializer):
    """O'qituvchi uchun — to'liq kontent CRUD."""

    class Meta:
        model  = TopicLevelContent
        fields = ('id', 'topic', 'level', 'video_url', 'lecture_text', 'resources', 'updated_at')
        read_only_fields = ('id', 'topic', 'updated_at')


class TopicLevelContentStudentSerializer(serializers.ModelSerializer):
    """Talaba uchun — o'qish uchun kontent (topic yashirin)."""

    class Meta:
        model  = TopicLevelContent
        fields = ('level', 'video_url', 'lecture_text', 'resources')


# ─── StudentLevelProgress ────────────────────────────────────────────────────

class StudentLevelProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model  = StudentLevelProgress
        fields = ('id', 'topic', 'level', 'video_watched', 'text_read', 'ad_awarded')
        read_only_fields = ('id', 'topic', 'ad_awarded')


class StudentLevelProgressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = StudentLevelProgress
        fields = ('video_watched', 'text_read')


# ─── LevelTest ───────────────────────────────────────────────────────────────

class LevelTestQuestionSerializer(serializers.ModelSerializer):
    """Talabaga savol — to'g'ri javob ko'rsatilmaydi."""

    class Meta:
        model  = LevelTestQuestion
        fields = ('id', 'question', 'options', 'order')


class LevelTestQuestionTeacherSerializer(serializers.ModelSerializer):
    """O'qituvchi uchun — to'g'ri javob va izoh ko'rsatiladi."""

    class Meta:
        model  = LevelTestQuestion
        fields = ('id', 'question', 'options', 'correct_answer', 'explanation', 'order')


class LevelTestSerializer(serializers.ModelSerializer):
    questions      = LevelTestQuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    ko_reward      = serializers.SerializerMethodField()
    is_locked      = serializers.SerializerMethodField()

    class Meta:
        model  = LevelTest
        fields = (
            'id', 'topic', 'level', 'title', 'pass_score',
            'question_count', 'ko_reward', 'is_active', 'is_locked', 'questions',
        )
        read_only_fields = ('id', 'topic')

    def get_question_count(self, obj):
        return obj.questions.count()

    def get_ko_reward(self, obj):
        return LevelTest.KO_SCORE_MAP.get(obj.level, 0)

    def get_is_locked(self, obj):
        """Test qulflangan? Oldingi daraja testi o'tilmagan bo'lsa."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return True
        if obj.level == 'beginner':
            return False
        try:
            ts = TopicScore.objects.get(student=request.user, topic=obj.topic)
            if obj.level == 'intermediate':
                return not ts.beginner_test_passed
            if obj.level == 'advanced':
                return not ts.intermediate_test_passed
        except TopicScore.DoesNotExist:
            return obj.level != 'beginner'
        return False


class LevelTestTeacherSerializer(LevelTestSerializer):
    questions = LevelTestQuestionTeacherSerializer(many=True, read_only=True)


class LevelTestSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.IntegerField(min_value=0, max_value=3),
        help_text='{question_id: selected_option_index}'
    )


class StudentLevelTestResultSerializer(serializers.ModelSerializer):
    level_test_title = serializers.CharField(source='level_test.title', read_only=True)
    level            = serializers.CharField(source='level_test.level', read_only=True)
    ko_reward        = serializers.SerializerMethodField()

    class Meta:
        model  = StudentLevelTestResult
        fields = (
            'id', 'level_test', 'level_test_title', 'level',
            'score', 'passed', 'ko_reward', 'attempt_no', 'completed_at',
        )
        read_only_fields = ('id', 'completed_at')

    def get_ko_reward(self, obj):
        if obj.passed:
            return LevelTest.KO_SCORE_MAP.get(obj.level_test.level, 0)
        return 0


# ─── Topic ───────────────────────────────────────────────────────────────────

class TopicMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Topic
        fields = ('id', 'number', 'title', 'difficulty', 'order')


class TopicSerializer(serializers.ModelSerializer):
    module_number = serializers.IntegerField(source='module.number', read_only=True)
    module_title  = serializers.CharField(source='module.title', read_only=True)
    test_count    = serializers.SerializerMethodField()
    task_count    = serializers.SerializerMethodField()
    content_count = serializers.SerializerMethodField()
    my_score      = serializers.SerializerMethodField()

    class Meta:
        model  = Topic
        fields = (
            'id', 'number', 'title', 'description', 'difficulty',
            'module', 'module_number', 'module_title',
            'is_active', 'order', 'created_at',
            'test_count', 'task_count', 'content_count', 'my_score',
        )
        read_only_fields = ('id', 'created_at')

    def get_test_count(self, obj):
        return obj.level_tests.filter(is_active=True).count()

    def get_task_count(self, obj):
        return {
            'exercise': obj.tasks.filter(task_category='exercise', is_active=True).count(),
            'project':  obj.tasks.filter(task_category='project',  is_active=True).count(),
        }

    def get_content_count(self, obj):
        """Nechta daraja uchun kontent kiritilgan (0–3)."""
        return obj.level_contents.count()

    def get_my_score(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        try:
            ts = TopicScore.objects.get(student=request.user, topic=obj)
            return TopicScoreSerializer(ts).data
        except TopicScore.DoesNotExist:
            return None


class TopicDetailSerializer(TopicSerializer):
    """Mavzu detail ko'rinishi — daraja kontentlari va testlar bilan."""
    level_contents  = serializers.SerializerMethodField()
    level_tests     = serializers.SerializerMethodField()
    my_progress     = serializers.SerializerMethodField()

    class Meta(TopicSerializer.Meta):
        fields = TopicSerializer.Meta.fields + ('level_contents', 'level_tests', 'my_progress')

    def get_level_contents(self, obj):
        request = self.context.get('request')
        contents = obj.level_contents.all()
        if request and request.user.is_authenticated and request.user.role in ('teacher', 'admin', 'superadmin'):
            return TopicLevelContentSerializer(contents, many=True, context=self.context).data
        return TopicLevelContentStudentSerializer(contents, many=True).data

    def get_level_tests(self, obj):
        request = self.context.get('request')
        tests   = obj.level_tests.filter(is_active=True)
        if request and request.user.is_authenticated and request.user.role in ('teacher', 'admin', 'superadmin'):
            return LevelTestTeacherSerializer(tests, many=True, context=self.context).data
        return LevelTestSerializer(tests, many=True, context=self.context).data

    def get_my_progress(self, obj):
        """Talabaning ushbu mavzudagi daraja progresslari."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        progresses = StudentLevelProgress.objects.filter(
            student=request.user, topic=obj
        )
        return StudentLevelProgressSerializer(progresses, many=True).data


# ─── TopicScore ───────────────────────────────────────────────────────────────

class TopicScoreSerializer(serializers.ModelSerializer):
    topic_title    = serializers.CharField(source='topic.title', read_only=True)
    topic_number   = serializers.IntegerField(source='topic.number', read_only=True)
    completion_pct = serializers.ReadOnlyField()

    class Meta:
        model  = TopicScore
        fields = (
            'id', 'topic', 'topic_title', 'topic_number', 'level',
            'mo_score', 'ko_score',
            'fa_score', 'fa_project_score',      # fa_score=avtomatik, fa_project=o'qituvchi
            're_score', 're_peer_score',          # re_score=avtomatik, re_peer=o'qituvchi
            'total_score', 'completion_pct',
            'beginner_test_passed', 'intermediate_test_passed', 'advanced_test_passed',
            'is_completed', 'attempt_count', 'completed_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'total_score', 'completion_pct',
            'beginner_test_passed', 'intermediate_test_passed', 'advanced_test_passed',
            'updated_at',
        )


class TopicScoreTeacherUpdateSerializer(serializers.ModelSerializer):
    """O'qituvchi MO ballini beradi (avtomatik, lekin o'qituvchi override qila oladi)."""

    class Meta:
        model  = TopicScore
        fields = ('mo_score',)

    def validate_mo_score(self, value):
        if value > 15:
            raise serializers.ValidationError('Motivatsion ball maksimum 15.')
        return value


class TopicScoreFaProjectUpdateSerializer(serializers.ModelSerializer):
    """O'qituvchi FA loyiha ballini beradi (max 10)."""

    class Meta:
        model  = TopicScore
        fields = ('fa_project_score',)

    def validate_fa_project_score(self, value):
        if value > 10:
            raise serializers.ValidationError('Loyiha ball maksimum 10.')
        return value


class TopicScoreRePeerUpdateSerializer(serializers.ModelSerializer):
    """O'qituvchi RE peer-review ballini beradi (max 10)."""

    class Meta:
        model  = TopicScore
        fields = ('re_peer_score',)

    def validate_re_peer_score(self, value):
        if value > 10:
            raise serializers.ValidationError('Peer-review ball maksimum 10.')
        return value


# ─── Task ────────────────────────────────────────────────────────────────────

class TaskSerializer(serializers.ModelSerializer):
    topic_title    = serializers.CharField(source='topic.title', read_only=True)
    fa_max         = serializers.SerializerMethodField()
    kr_max         = serializers.SerializerMethodField()

    class Meta:
        model  = Task
        fields = (
            'id', 'topic', 'topic_title',
            'level', 'task_category', 'task_type',
            'title', 'description', 'starter_code',
            'test_cases', 'time_limit_ms', 'memory_limit_mb',
            'max_score', 'fa_max', 'kr_max',
            'order', 'is_active', 'created_at',
        )
        read_only_fields = ('id', 'created_at')
        extra_kwargs = {'expected_output': {'write_only': True}}

    def get_fa_max(self, obj):
        if obj.task_category == 'exercise':
            return Task.FA_LEVEL_MAX.get(obj.level, 0)
        return None

    def get_kr_max(self, obj):
        if obj.task_category == 'project':
            return Task.KR_LEVEL_MAX.get(obj.level, 0)
        return None


class TaskStudentSerializer(TaskSerializer):
    """Talabalar uchun — test_cases va expected_output yashirin."""
    class Meta(TaskSerializer.Meta):
        extra_kwargs = {
            'expected_output': {'write_only': True},
            'test_cases':      {'write_only': True},
        }


# ─── Submission ───────────────────────────────────────────────────────────────

class SubmissionSerializer(serializers.ModelSerializer):
    task_title   = serializers.CharField(source='task.title', read_only=True)
    task_level   = serializers.CharField(source='task.level', read_only=True)
    task_category = serializers.CharField(source='task.task_category', read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model  = Submission
        fields = (
            'id', 'task', 'task_title', 'task_level', 'task_category', 'student_name',
            'code', 'language', 'status',
            'runtime_ms', 'memory_kb', 'test_results',
            'score_awarded', 'error_message', 'submitted_at',
        )
        read_only_fields = (
            'id', 'status', 'runtime_ms', 'memory_kb',
            'test_results', 'score_awarded', 'error_message', 'submitted_at',
        )

    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username


class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Submission
        fields = ('task', 'code', 'language')


# ─── DiagnosticTest ───────────────────────────────────────────────────────────

class DiagnosticTestSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DiagnosticTest
        fields = ('id', 'score', 'level', 'completed_at')
        read_only_fields = ('id', 'score', 'level', 'completed_at')


class DiagnosticTestSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(child=serializers.IntegerField())


# ─── ReflectionJournal ───────────────────────────────────────────────────────

class ReflectionJournalSerializer(serializers.ModelSerializer):
    topic_title = serializers.CharField(source='topic.title', read_only=True)

    class Meta:
        model  = ReflectionJournal
        fields = ('id', 'topic', 'topic_title', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
