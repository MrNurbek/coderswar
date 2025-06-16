from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Importlar: viewlar
from api.comment.views import CommentListAPIView, CommentCreateAPIView
from api.contact.views import ContactView, EmailSubmissionView
from api.content.views import ContentListAPIView
from api.duels.views import CreateDuelView, JoinDuelView, DuelListView, DuelAssignmentSubmitView, DuelAssignmentsView
from api.initialtest.view import InitialTestListView, InitialTestSubmitView
from api.mainquest.views import TopicListAPIView, TopicDetailAPIView, MarkTopicCompletedAPIView
from api.sidequest.views import AssignmentSubmitView, DropGearView, AssignmentListView, AssignmentDetailView
from api.userapp.views import (
    RegisterView, AcceptView, LoginView, UserProfileView, UpdateUserProfileView,
    ChangePasswordView, ForgotPasswordView, ResetPasswordView, CharacterListView,
    TopicListView, UserRatingListView, ChoicesAPIView, TopicSimpleListAPIView, TopicPlansAPIView, PlanDetailAPIView
)

# Swagger schema
schema_view = get_schema_view(
    openapi.Info(
        title="CodersWar API",
        default_version='v1',
        description="CodersWar loyihasi uchun API hujjatlari",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="your-email@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# 🔁 Set_language uchun kerak
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# 🌐 ADMIN panel va boshqa i18n kerak bo'lgan sahifalar
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
)

# 📡 API va boshqa yo'llar (i18n bilan bog‘liq emas)
urlpatterns += [

    # Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('accept/', AcceptView.as_view(), name='accept'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),

    # User profile
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', UpdateUserProfileView.as_view(), name='update-profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),

    # Content
    path('content/', ContentListAPIView.as_view(), name='content-list'),

    # Topics
    # path('topics/<int:pk>/', TopicDetailAPIView.as_view(), name='topic-detail'),

    # path('api/topics/', TopicListAPIView.as_view(), name='topic-list'),
    # path('topics/', TopicListView.as_view(), name='topics'),

    path('topics/', TopicSimpleListAPIView.as_view(), name='topic-simple-list'),
    path('topics/<int:pk>/plans/', TopicPlansAPIView.as_view(), name='topic-plans'),
    path('plans/<int:pk>/', PlanDetailAPIView.as_view(), name='plan-detail'),
    path('topics/<int:pk>/complete/', MarkTopicCompletedAPIView.as_view(), name='mark-topic-complete'),

    # Comments
    path('api/comments/', CommentListAPIView.as_view(), name='comment-list'),
    path('api/comments/create/', CommentCreateAPIView.as_view(), name='comment-create'),

    # Characters and choices
    path('characters/', CharacterListView.as_view(), name='characters'),
    path('api/choices/', ChoicesAPIView.as_view(), name='choices'),

    # Assignments
    path('assignments/', AssignmentListView.as_view(), name='assignment-list'),
    path('assignments/<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/<int:assignment_id>/submit/', AssignmentSubmitView.as_view(), name='assignment-submit'),
    path('gear/drop/', DropGearView.as_view(), name='gear-drop'),

    # Contact
    path('contact/', ContactView.as_view(), name='contact'),
    path('submit-email/', EmailSubmissionView.as_view(), name='submit-email'),

    # Duel
    path('duel/create/', CreateDuelView.as_view(), name='duel-create'),
    path('duel/<int:duel_id>/join/', JoinDuelView.as_view(), name='duel-join'),
    path('duel/available/', DuelListView.as_view(), name='duel-available-list'),
    path('duel/<int:duel_id>/assignments/', DuelAssignmentsView.as_view(), name='duel-assignments'),
    path('duel/<int:duel_id>/submit/', DuelAssignmentSubmitView.as_view(), name='duel-assignment-submit'),

    # Rating
    path('users/rating/', UserRatingListView.as_view(), name='user-rating'),

    # Initial test
    path('initial-tests/', InitialTestListView.as_view(), name='initial-test-list'),
    path('initial-tests/submit/', InitialTestSubmitView.as_view(), name='initial-test-submit'),
]

# 📁 Statik va media fayllar
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
