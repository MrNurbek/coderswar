from django.contrib import admin

from apps.mainquest.models import Topic, CodeExample, Plan, Assignment, UserProgress, AssignmentStatus


#
# admin.site.register(Topic)
# admin.site.register(Plan)
# admin.site.register(CodeExample)
# admin.site.register(Assignment)
# admin.site.register(AssignmentStatus)
# admin.site.register(UserProgress)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    search_fields = ['title']
    ordering = ['order']


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic']
    search_fields = ['title', 'text']
    list_filter = ['topic']


@admin.register(CodeExample)
class CodeExampleAdmin(admin.ModelAdmin):
    list_display = ['plan']
    search_fields = ['code']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'plan', 'order')
    list_filter = ('plan',)
    search_fields = ('title', 'task_description', 'sample_input', 'expected_output')
    ordering = ('plan', 'order')


@admin.register(AssignmentStatus)
class AssignmentStatusAdmin(admin.ModelAdmin):
    list_display = ['user', 'assignment', 'is_completed', 'earned_points']
    list_filter = ['is_completed']
    search_fields = ['user__email']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'is_completed', 'completed_at']
    list_filter = ['is_completed']
    search_fields = ['user__email', 'topic__title']
