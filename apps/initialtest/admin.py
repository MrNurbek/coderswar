from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import InitialTest, InitialTestAnswer

class InitialTestAnswerInline(admin.TabularInline):
    model = InitialTestAnswer
    extra = 1

@admin.register(InitialTest)
class InitialTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'order')
    inlines = [InitialTestAnswerInline]

@admin.register(InitialTestAnswer)
class InitialTestAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'answer_text', 'is_correct')
    list_filter = ('is_correct',)
