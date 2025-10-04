# helpdesk_mini/tickets/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# 1. Define how the CustomUser model should look in the Admin
class CustomUserAdmin(UserAdmin):
    # This ensures the 'role' field is visible when creating/editing a user
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    # This makes the 'role' visible in the main User list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')

# 2. Register the CustomUser model with the CustomUserAdmin configuration
admin.site.register(CustomUser, CustomUserAdmin)