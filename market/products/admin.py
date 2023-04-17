from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from products.models import Category, Product, ProductImage, ProductProperty, Property


class CategoryAdmin(DjangoMpttAdmin):
    """Регистрация модели Категория в админке"""
    list_display = ['name']


class ImageInline(admin.StackedInline):
    """Добавление изображения в админке модели Product"""
    model = ProductImage


class ProductPropertyInline(admin.StackedInline):
    """Добавление свойства в админке модели Product"""
    model = ProductProperty


class PropertyAdmin(admin.ModelAdmin):
    """Регистрация модели Property в админке"""
    list_display = 'id', 'name'


class ProductAdmin(admin.ModelAdmin):
    """Регистрация модели Product в админке"""
    list_display = 'id', 'name', 'category'
    inlines = [ProductPropertyInline, ImageInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Product, ProductAdmin)
