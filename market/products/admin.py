from django.contrib import admin
from products.models import Category


class CategoryAdmin(admin.ModelAdmin):
    """Регистрация модели Категория в админке"""
    list_display = ['name', 'is_active', 'product']
    list_filter = ['is_active', ]


admin.site.register(Category, CategoryAdmin)
