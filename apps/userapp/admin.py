from django.contrib import admin

from apps.userapp.models import User, ConfirmCode

admin.site.register(User)
admin.site.register(ConfirmCode)