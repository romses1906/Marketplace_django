from django.contrib import admin
from .models import Banner


class BannerAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
     и поведения модели баннера в Django Admin."""
    list_display = ('title', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'description',)

    def get_queryset(self, request):
        """Фильтрует список и включает только активные баннеры."""
        return Banner.objects.get_active_banners()


admin.site.register(Banner, BannerAdmin)
