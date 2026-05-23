from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPCode, Group, GroupMembership, StudentProfile, TeacherProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('username', 'email', 'get_full_name', 'role', 'is_verified', 'date_joined')
    list_filter   = ('role', 'is_verified', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Platforma', {'fields': ('role', 'phone', 'bio', 'avatar', 'is_verified')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Platforma', {'fields': ('role', 'email', 'first_name', 'last_name')}),
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display  = ('user', 'code', 'is_used', 'expires_at', 'created_at')
    list_filter   = ('is_used',)
    search_fields = ('user__email', 'code')
    readonly_fields = ('created_at',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display  = ('name', 'code', 'teacher', 'year', 'faculty')
    list_filter   = ('year', 'faculty')
    search_fields = ('name', 'code', 'teacher__username')


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display  = ('student', 'group', 'joined_at')
    list_filter   = ('group',)
    search_fields = ('student__username', 'group__name')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display   = ('user', 'character', 'level', 'rating_score', 'academic_score',
                      'current_streak', 'max_streak', 'last_active')
    list_filter    = ('level', 'character')
    search_fields  = ('user__username', 'user__email')
    readonly_fields = ('updated_at',)

    actions = ['recalculate_scores']

    @admin.action(description='Balllarni qayta hisoblash')
    def recalculate_scores(self, request, queryset):
        for profile in queryset:
            profile.recalculate()
        self.message_user(request, f'{queryset.count()} profil yangilandi.')


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'department', 'university', 'title')
    search_fields = ('user__username', 'department', 'university')
