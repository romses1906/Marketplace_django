from django.contrib import admin
from .models import SiteSettings


class SiteSettingsAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели настроек сайта в Django Admin."""
    list_display = ('min_order_price_for_free_shipping',
                    'standard_order_price', 'express_order_price', 'banners_count',
                    'top_product_count', 'limited_edition_count', 'hot_deals',
                    'product_cache_time', )


admin.site.register(SiteSettings, SiteSettingsAdmin)
