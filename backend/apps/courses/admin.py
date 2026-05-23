from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Module, Topic, TopicLevelContent,
    LevelTest, LevelTestQuestion, StudentLevelTestResult,
    StudentLevelProgress, TopicScore,
    Task, Submission, DiagnosticTest, ReflectionJournal,
)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display  = ('number', 'title', 'is_active')
    list_editable = ('is_active',)
    ordering      = ('number',)


# ── Topic ────────────────────────────────────────────────────────────────────

class TopicLevelContentInline(admin.StackedInline):
    model       = TopicLevelContent
    extra       = 0
    max_num     = 3
    fields      = ('level', 'video_url', 'lecture_text', 'resources', 'created_by')
    readonly_fields = ('created_by',)
    show_change_link = True

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            existing = obj.level_contents.count()
            return max(0, 3 - existing)
        return 3


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display  = ('number', 'title', 'module', 'difficulty', 'content_status', 'test_count', 'task_count', 'is_active', 'order')
    list_filter   = ('module', 'difficulty', 'is_active')
    search_fields = ('title',)
    list_editable = ('is_active', 'order')
    ordering      = ('number',)
    inlines       = [TopicLevelContentInline]

    def content_status(self, obj):
        levels = obj.level_contents.values_list('level', flat=True)
        icons  = {'beginner': '🟡', 'intermediate': '🟠', 'advanced': '🔴'}
        badges = ' '.join(icons.get(l, '⚪') for l in sorted(levels))
        color  = 'green' if len(levels) == 3 else 'orange' if len(levels) > 0 else 'red'
        return format_html('<span style="color:{}">{} ({}/3)</span>', color, badges, len(levels))
    content_status.short_description = 'Kontentlar'

    def test_count(self, obj):
        c     = obj.level_tests.count()
        color = 'green' if c == 3 else 'orange' if c > 0 else 'red'
        return format_html('<span style="color:{}">{}/3 test</span>', color, c)
    test_count.short_description = 'Testlar'

    def task_count(self, obj):
        exercises = obj.tasks.filter(task_category='exercise').count()
        projects  = obj.tasks.filter(task_category='project').count()
        return format_html('{}💪 {}🚀', exercises, projects)
    task_count.short_description = 'Topshiriqlar'


# ── TopicLevelContent ────────────────────────────────────────────────────────

@admin.register(TopicLevelContent)
class TopicLevelContentAdmin(admin.ModelAdmin):
    list_display    = ('topic', 'level', 'has_video', 'has_text', 'resource_count', 'created_by', 'updated_at')
    list_filter     = ('level', 'topic__module')
    search_fields   = ('topic__title',)
    readonly_fields = ('created_at', 'updated_at')
    ordering        = ('topic__number', 'level')

    def has_video(self, obj):
        return bool(obj.video_url)
    has_video.boolean = True
    has_video.short_description = 'Video'

    def has_text(self, obj):
        return len(obj.lecture_text) > 50
    has_text.boolean = True
    has_text.short_description = 'Matn'

    def resource_count(self, obj):
        return len(obj.resources) if obj.resources else 0
    resource_count.short_description = 'Resurslar'

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ── LevelTest & Questions ─────────────────────────────────────────────────────

class LevelTestQuestionInline(admin.TabularInline):
    model    = LevelTestQuestion
    extra    = 10
    max_num  = 10
    fields   = ('order', 'question', 'options', 'correct_answer', 'explanation')
    ordering = ('order',)


@admin.register(LevelTest)
class LevelTestAdmin(admin.ModelAdmin):
    list_display    = ('topic', 'level', 'title', 'question_count', 'pass_score', 'is_active', 'created_by')
    list_filter     = ('level', 'is_active', 'topic__module')
    search_fields   = ('title', 'topic__title')
    list_editable   = ('is_active',)
    inlines         = [LevelTestQuestionInline]
    readonly_fields = ('created_at',)

    def question_count(self, obj):
        c     = obj.questions.count()
        color = 'green' if c == 10 else 'orange' if c > 0 else 'red'
        return format_html('<span style="color:{}">{}/10</span>', color, c)
    question_count.short_description = 'Savollar'

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(LevelTestQuestion)
class LevelTestQuestionAdmin(admin.ModelAdmin):
    list_display  = ('test', 'order', 'short_question', 'correct_answer')
    list_filter   = ('test__level', 'test__topic__module')
    search_fields = ('question', 'test__title')
    ordering      = ('test', 'order')

    def short_question(self, obj):
        return obj.question[:80]
    short_question.short_description = 'Savol'


@admin.register(StudentLevelTestResult)
class StudentLevelTestResultAdmin(admin.ModelAdmin):
    list_display    = ('student', 'level_test', 'score', 'passed', 'attempt_no', 'completed_at')
    list_filter     = ('passed', 'level_test__level', 'level_test__topic__module')
    search_fields   = ('student__username', 'level_test__title')
    readonly_fields = ('completed_at', 'answers')


# ── StudentLevelProgress ─────────────────────────────────────────────────────

@admin.register(StudentLevelProgress)
class StudentLevelProgressAdmin(admin.ModelAdmin):
    list_display   = ('student', 'topic', 'level', 'video_watched', 'text_read', 'ad_awarded')
    list_filter    = ('level', 'ad_awarded', 'topic__module')
    search_fields  = ('student__username', 'topic__title')
    readonly_fields = ()


# ── TopicScore ────────────────────────────────────────────────────────────────

@admin.register(TopicScore)
class TopicScoreAdmin(admin.ModelAdmin):
    list_display    = (
        'student', 'topic', 'level', 'total_score',
        'mo_score', 'ko_score', 'fa_score', 're_score',
        'tests_passed', 'is_completed',
    )
    list_filter     = ('is_completed', 'level', 'topic__module')
    search_fields   = ('student__username', 'topic__title')
    readonly_fields = ('total_score', 'updated_at', 'completion_pct')

    def tests_passed(self, obj):
        b = '✓' if obj.beginner_test_passed else '✗'
        o = '✓' if obj.intermediate_test_passed else '✗'
        y = '✓' if obj.advanced_test_passed else '✗'
        return format_html('B:{} O:{} Y:{}', b, o, y)
    tests_passed.short_description = 'Testlar'

    actions = ['recalculate_scores', 'give_mo_score']

    @admin.action(description="Mo'(motivatsion) ballini berish — +15")
    def give_mo_score(self, request, queryset):
        queryset.update(mo_score=15)
        for ts in queryset:
            ts.save()
        self.message_user(request, f'{queryset.count()} ta yozuvga MO=15 berildi.')

    @admin.action(description='Balllarni qayta hisoblash')
    def recalculate_scores(self, request, queryset):
        for ts in queryset:
            ts.save()
        self.message_user(request, f'{queryset.count()} ta yozuv yangilandi.')


# ── Task, Submission, Diagnostic, Reflection ─────────────────────────────────

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ('title', 'topic', 'level', 'task_category', 'task_type', 'max_score', 'is_active', 'order')
    list_filter   = ('level', 'task_category', 'task_type', 'is_active', 'topic__module')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'order')
    ordering      = ('topic__number', 'level', 'task_category', 'order')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display    = ('student', 'task', 'status', 'score_awarded', 'runtime_ms', 'submitted_at')
    list_filter     = ('status', 'language')
    search_fields   = ('student__username', 'task__title')
    readonly_fields = ('submitted_at', 'judge0_token', 'test_results')
    ordering        = ('-submitted_at',)


@admin.register(DiagnosticTest)
class DiagnosticTestAdmin(admin.ModelAdmin):
    list_display    = ('student', 'level', 'score', 'completed_at')
    list_filter     = ('level',)
    readonly_fields = ('completed_at', 'answers')


@admin.register(ReflectionJournal)
class ReflectionJournalAdmin(admin.ModelAdmin):
    list_display    = ('student', 'topic', 'created_at', 'updated_at')
    search_fields   = ('student__username', 'topic__title')
    readonly_fields = ('created_at', 'updated_at')
