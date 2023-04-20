from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import User
from .forms import CustomUserCreationForm


class UserRegAdmin(UserAdmin):
    """Регистрация модели User в админке"""
    add_form = CustomUserCreationForm
    model = User
    list_display = 'email', 'is_superuser', 'is_active'


admin.site.register(User, UserRegAdmin)
