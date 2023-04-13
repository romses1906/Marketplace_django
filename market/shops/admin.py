from django.contrib import admin
from .models import Shop


class ShopAdmin(admin.ModelAdmin):
    """ Модель для отображения модели Shop в админке. """
    list_display = ("name", "phone_number", "email")



admin.site.register(Shop, ShopAdmin)
