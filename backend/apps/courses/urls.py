from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from .views import (
    ModuleListView,
    TopicViewSet, TopicLevelContentViewSet, StudentLevelProgressView,
    LevelTestViewSet,
    TopicScoreViewSet,
    TaskViewSet, SubmissionViewSet,
    DiagnosticTestView, ReflectionJournalViewSet,
    AITeacherReportView,
)

# ── Asosiy router ──────────────────────────────────────────────────────────
router = DefaultRouter()
router.register('topics',      TopicViewSet,           basename='topic')
router.register('scores',      TopicScoreViewSet,      basename='score')
router.register('tasks',       TaskViewSet,            basename='task')
router.register('submissions', SubmissionViewSet,      basename='submission')
router.register('reflections', ReflectionJournalViewSet, basename='reflection')

# ── Nested: topics/{topic_pk}/contents/   &   topics/{topic_pk}/tests/ ────
topics_router = nested_routers.NestedDefaultRouter(router, 'topics', lookup='topic')
topics_router.register('contents', TopicLevelContentViewSet, basename='topic-content')
topics_router.register('tests',    LevelTestViewSet,         basename='topic-test')

urlpatterns = [
    path('modules/',    ModuleListView.as_view(),     name='module_list'),
    path('diagnostic/', DiagnosticTestView.as_view(), name='diagnostic'),
    path('ai-report/',  AITeacherReportView.as_view(), name='ai_report'),

    # Talaba daraja progressi
    path('topics/<int:topic_pk>/my-progress/', StudentLevelProgressView.as_view(), name='level_progress'),

    path('', include(router.urls)),
    path('', include(topics_router.urls)),
]
