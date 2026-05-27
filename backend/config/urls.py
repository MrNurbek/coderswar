from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
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

# Local dev: frontend HTML fayllarini Django orqali serve qilish
# Production da Nginx buni o'zi bajaradi
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^(?P<path>[a-z0-9_-]+\.html)$', static_serve,
                {'document_root': settings.FRONTEND_DIR}),
        path('', static_serve,
             {'document_root': settings.FRONTEND_DIR, 'path': 'index.html'}),
    ]
