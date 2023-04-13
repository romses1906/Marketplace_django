from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from products.models import Category


class CategoryAdmin(DjangoMpttAdmin):
    """Регистрация модели Категория в админке"""
    list_display = ['name']


admin.site.register(Category, CategoryAdmin)
