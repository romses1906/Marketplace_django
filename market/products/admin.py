from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from products.models import Category, Product, ProductImage, ProductProperty, Property, ProductTag


class CategoryAdmin(DjangoMpttAdmin):
    """Регистрация модели Категория в админке"""
    list_display = ['name']
    ordering = 'name',


class ImageInline(admin.StackedInline):
    """Добавление изображения в админке модели Product"""
    model = ProductImage


class ProductPropertyInline(admin.StackedInline):
    """Добавление свойства в админке модели Product"""
    model = ProductProperty


class PropertyAdmin(admin.ModelAdmin):
    """Регистрация модели Property в админке"""
    list_display = 'name',
    ordering = 'name',


class ProductAdmin(admin.ModelAdmin):
    """Регистрация модели Product в админке"""
    list_display = 'name', 'category'
    list_filter = 'name', 'created', 'category'
    search_fields = 'name', 'category'
    inlines = [ProductPropertyInline, ImageInline]
    ordering = 'name',


class ProductTagAdmin(admin.ModelAdmin):
    """Регистрация модели ProductTag в админке"""
    list_display = ['tag_list']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    @staticmethod
    def tag_list(obj):
        return u", ".join(o.name for o in obj.tags.all())


admin.site.register(Category, CategoryAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductTag, ProductTagAdmin)
