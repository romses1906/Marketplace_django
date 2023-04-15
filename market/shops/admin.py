from django.contrib import admin

from .models import Banner, Shop


class BannerAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
     и поведения модели баннера в Django Admin."""
    list_display = ('title', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'description',)

    def get_queryset(self, request):
        """Фильтрует список и включает только активные баннеры."""
        return Banner.objects.get_active_banners()


class ShopAdmin(admin.ModelAdmin):
    """ Модель для отображения модели Shop в админке. """
    list_display = ("name", "phone_number", "email")


admin.site.register(Shop, ShopAdmin)
admin.site.register(Banner, BannerAdmin)
