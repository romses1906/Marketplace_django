from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import User


class UserRegAdmin(UserAdmin):
    """Регистрация модели User в админке"""
    list_display = 'email', 'is_superuser', 'is_active'


admin.site.register(User, UserRegAdmin)
