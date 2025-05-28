from django.contrib import admin

from apps.sidequest.models import GearItem, UserGear

# Register your models here.
admin.site.register(GearItem)
admin.site.register(UserGear)