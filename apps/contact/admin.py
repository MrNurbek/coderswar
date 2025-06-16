from django.contrib import admin

from apps.contact.models import ContactMessage, EmailSubmission

# Register your models here.
admin.site.register(ContactMessage)
admin.site.register(EmailSubmission)