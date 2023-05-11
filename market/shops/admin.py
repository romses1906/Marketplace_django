from django.contrib import admin

from .models import Banner, Shop, Offer


class BannerAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
     и поведения модели баннера в Django Admin."""
    list_display = ('title', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'description',)


class ShopAdmin(admin.ModelAdmin):
    """ Модель для отображения модели Shop в админке. """
    list_display = ("name", "phone_number", "email")


class OfferAdmin(admin.ModelAdmin):
    """ Модель для отображения модели Offer в админке. """
    list_display = "shop", "product", "price", "in_stock"


admin.site.register(Shop, ShopAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Offer, OfferAdmin)
