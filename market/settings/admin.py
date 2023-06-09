from django.contrib import admin
from .models import SiteSettings, Discount, DiscountOnCart, DiscountOnSet, ProductInDiscountOnSet


class SiteSettingsAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели настроек сайта в Django Admin."""
    list_display = ('min_order_price_for_free_shipping',
                    'standard_order_price', 'express_order_price', 'banners_count',
                    'top_product_count', 'limited_edition_count', 'hot_deals',
                    'product_cache_time',)


class DiscountAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели скидок на товары в Django Admin."""

    list_display = ('name', 'description', 'start_date', 'end_date', 'value', 'value_type', 'active',)


class DiscountOnCartAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели скидок на корзину в Django Admin."""

    list_display = ('name', 'description', 'start_date', 'end_date', 'value', 'value_type', 'active', 'quantity_at',
                    'quantity_at', 'cart_total_price_at',)


class DiscountOnSetAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели скидок на набор товаров в Django Admin."""

    list_display = ('name', 'description', 'start_date', 'end_date', 'value', 'value_type', 'active',)


class ProductInDiscountOnSetAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели товаров из наборов со скидкой в Django Admin."""

    list_display = ('product', 'discount',)


admin.site.register(SiteSettings, SiteSettingsAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(DiscountOnCart, DiscountOnCartAdmin)
admin.site.register(DiscountOnSet, DiscountOnSetAdmin)
admin.site.register(ProductInDiscountOnSet, ProductInDiscountOnSetAdmin)
