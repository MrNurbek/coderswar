from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/', include('apps.users.urls')),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Core
    path('api/courses/', include('apps.courses.urls')),
    path('api/game/', include('apps.gamification.urls')),
    path('api/social/', include('apps.social.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
