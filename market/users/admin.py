from django.contrib import admin
from .models import Part, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	"""Регистрация модели User в админке"""
	list_display = 'username', 'is_superuser', 'is_active'


admin.site.register(Part)
