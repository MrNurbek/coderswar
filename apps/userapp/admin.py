from django.contrib import admin

from apps.userapp.models import User, ConfirmCode, CharacterClass

admin.site.register(User)
admin.site.register(ConfirmCode)
admin.site.register(CharacterClass)