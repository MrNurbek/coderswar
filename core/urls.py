
from django.contrib import admin
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter

from api.comment.views import CommentListAPIView, CommentCreateAPIView
from api.content.views import ContentListAPIView
from api.mainquest.views import TopicListAPIView, TopicDetailAPIView, MarkTopicCompletedAPIView
from core import settings
from django.conf.urls.static import static
from api.userapp.views import RegisterView, AcceptView, LoginView, UserProfileView, UpdateUserProfileView, \
    ChangePasswordView, ForgotPasswordView, ResetPasswordView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi





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



urlpatterns = [
                  path('admin/', admin.site.urls),
                  re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
                          name='schema-json'),
                  path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                  path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


                  path('register/', RegisterView.as_view(), name='register'),
                  path('accept/', AcceptView.as_view(), name='accept'),
                  path('login/', LoginView.as_view(), name='login'),
                  path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
                  path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
                  path('profile/', UserProfileView.as_view(), name='user-profile'),
                  path('profile/update/', UpdateUserProfileView.as_view(), name='update-profile'),
                  path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
                  path('content/', ContentListAPIView.as_view(), name='content-list'),

                  path('topics/<int:pk>/', TopicDetailAPIView.as_view(), name='topic-detail'),
                  path('topics/<int:pk>/complete/', MarkTopicCompletedAPIView.as_view(), name='mark-topic-complete'),
                  path('api/topics/', TopicListAPIView.as_view(), name='topic-list'),
                  path('api/comments/', CommentListAPIView.as_view(), name='comment-list'),
                  path('api/comments/create/', CommentCreateAPIView.as_view(), name='comment-create'),


              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)
