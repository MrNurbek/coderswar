from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Duel, DuelAssignment

@admin.register(Duel)
class DuelAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'opponent', 'created_at', 'is_active', 'winner')
    list_filter = ('is_active', 'created_at')
    search_fields = ('creator__email', 'opponent__email')

@admin.register(DuelAssignment)
class DuelAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'duel', 'assignment')
    list_filter = ('duel',)
    search_fields = ('assignment__title',)