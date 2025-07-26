from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_officer', 'language')
    list_filter = ('is_officer', 'language', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('mobile', 'address', 'language', 'is_officer')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'classes': ('wide',),
            'fields': ('mobile', 'address', 'language', 'is_officer'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'mobile')
    ordering = ('username',)

admin.site.register(User, CustomUserAdmin)
