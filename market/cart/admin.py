from django.contrib import admin
from cart.models import Delivery, Order, OrderItem


class DeliveryAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели доставки в Django Admin."""
    list_display = ('delivery_option', 'delivery_fee', 'order_total_for_free_delivery')


class OrderItemInline(admin.TabularInline):
    """Используется для редактирования экземпляров
    OrderItem в модели Order в Django Admin."""
    model = OrderItem
    raw_id_fields = ('offer',)


class OrderAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели заказа в Django Admin."""
    list_display = ('id', 'user', 'created', 'updated', 'status', 'payment_date',
                    'delivery', 'delivery_address', 'get_total_cost')
    list_filter = ('status', 'created', 'updated')
    inlines = [OrderItemInline]
    search_fields = ('user__username', 'delivery_address')


class OrderItemAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели позиции заказа в Django Admin."""
    list_display = ('id', 'order', 'offer', 'quantity', 'get_cost')
    list_filter = ('order__status', 'date_added')
    search_fields = ('offer__product',)


admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
