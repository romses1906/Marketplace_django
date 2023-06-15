from django.contrib import admin
from .models import SiteSettings, Discount, DiscountOnCart, DiscountOnSet, ProductInDiscountOnSet


class SiteSettingsAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели настроек сайта в Django Admin."""
    list_display = ('min_order_price_for_free_shipping',
                    'standard_order_price', 'express_order_price', 'banners_count',
                    'top_product_count', 'limited_edition_count', 'hot_deals',
                    'product_cache_time',)


class DiscountActiveMixin:
    def discounts_is_active(self, request, queryset):
        queryset.update(active=True)

    def discounts_is_passive(self, request, queryset):
        queryset.update(active=False)

    discounts_is_active.short_description = 'Перевести в статус "активно"'
    discounts_is_passive.short_description = 'Перевести в статус "неактивно"'


class ProductInDiscountOnSetInline(admin.StackedInline):
    """Добавление товара в скидочный набор в админке модели DiscountOnSet"""

    model = ProductInDiscountOnSet


class DiscountAdmin(admin.ModelAdmin, DiscountActiveMixin):
    """Используется для настройки отображения
         и поведения модели скидок на товары в Django Admin."""

    list_display = ('name', 'description', 'start_date', 'end_date', 'value', 'value_type', 'active',)
    actions = ['discounts_is_active', 'discounts_is_passive']


class DiscountOnCartAdmin(admin.ModelAdmin, DiscountActiveMixin):
    """Используется для настройки отображения
         и поведения модели скидок на корзину в Django Admin."""

    list_display = ('name', 'description', 'start_date', 'end_date', 'value', 'value_type', 'active', 'quantity_at',
                    'quantity_at', 'cart_total_price_at',)
    actions = ['discounts_is_active', 'discounts_is_passive']


class DiscountOnSetAdmin(admin.ModelAdmin, DiscountActiveMixin):
    """Используется для настройки отображения
         и поведения модели скидок на набор товаров в Django Admin."""

    list_display = ('name', 'description', 'start_date', 'end_date', 'value', 'value_type', 'active',)
    actions = ['discounts_is_active', 'discounts_is_passive']
    inlines = [ProductInDiscountOnSetInline]


class ProductInDiscountOnSetAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели товаров из наборов со скидкой в Django Admin."""

    list_display = ('product', 'discount',)


admin.site.register(SiteSettings, SiteSettingsAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(DiscountOnCart, DiscountOnCartAdmin)
admin.site.register(DiscountOnSet, DiscountOnSetAdmin)
admin.site.register(ProductInDiscountOnSet, ProductInDiscountOnSetAdmin)
