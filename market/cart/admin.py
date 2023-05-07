from django.contrib import admin

from cart.models import Cart, ProductInCart


class ProductInCartInline(admin.TabularInline):
    """Используется для редактирования экземпляров
    ProductInCart в модели Cart в Django Admin."""
    model = ProductInCart


class CartAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели корзины в Django Admin."""
    list_display = ('id', 'user', 'is_active')


class ProductInCartAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели позиций корзины в Django Admin."""
    list_display = ('offer', 'cart', 'quantity', 'date_added')


admin.site.register(Cart, CartAdmin)
admin.site.register(ProductInCart, ProductInCartAdmin)
