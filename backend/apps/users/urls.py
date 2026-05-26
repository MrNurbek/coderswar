from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    MyTokenObtainPairView, RegisterView, OTPVerifyView, ResendOTPView,
    MeView, PasswordChangeView, AvatarUploadView,
    ForgotPasswordView, ResetPasswordView,
    AdminUserBlockView,
    StudentListView, StudentProfileView,
    GroupViewSet,
)
from .admin_views import server_status_view, system_logs_view

router = DefaultRouter()
router.register('groups', GroupViewSet, basename='group')

urlpatterns = [
    # Auth
    path('token/',             MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/',     TokenRefreshView.as_view(),      name='token_refresh'),
    path('register/',          RegisterView.as_view(),          name='register'),
    path('verify-otp/',        OTPVerifyView.as_view(),         name='verify_otp'),
    path('resend-otp/',        ResendOTPView.as_view(),         name='resend_otp'),
    path('forgot-password/',   ForgotPasswordView.as_view(),    name='forgot_password'),
    path('reset-password/',    ResetPasswordView.as_view(),     name='reset_password'),

    # Profile
    path('me/',             MeView.as_view(),           name='me'),
    path('me/password/',    PasswordChangeView.as_view(), name='password_change'),
    path('me/avatar/',      AvatarUploadView.as_view(),  name='avatar_upload'),

    # Students
    path('students/',                        StudentListView.as_view(),    name='student_list'),
    path('students/<int:user_id>/profile/',  StudentProfileView.as_view(), name='student_profile'),

    # Admin actions
    path('users/<int:user_id>/<str:action>/', AdminUserBlockView.as_view(), name='admin_user_action'),

    # Admin monitoring
    path('admin/server-status/', server_status_view, name='admin_server_status'),
    path('admin/system-logs/',   system_logs_view,   name='admin_system_logs'),

    # Groups
    path('', include(router.urls)),
]
