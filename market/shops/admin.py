from django.contrib import admin
from .models import Banner


class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'description',)

    def get_queryset(self, request):
        return Banner.objects.get_active_banners()


admin.site.register(Banner, BannerAdmin)
