from django.contrib import admin

from apps.mainquest.models import Topic, CodeExample, Plan, Assignment, UserProgress

admin.site.register(Topic)
admin.site.register(Plan)
admin.site.register(CodeExample)
admin.site.register(Assignment)
admin.site.register(UserProgress)

