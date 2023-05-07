from django.contrib import admin
from order.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Используется для редактирования экземпляров
    OrderItem в модели Order в Django Admin."""
    model = OrderItem
    raw_id_fields = ('offer',)


class OrderAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели заказа в Django Admin."""
    list_display = ('id', 'user', 'full_name', 'created', 'updated', 'status', 'payment_date',
                    'delivery_option', 'delivery_address', 'delivery_city', 'payment_option', 'total_cost')
    list_filter = ('status', 'created', 'updated')
    inlines = [OrderItemInline]
    search_fields = ('user__username', 'delivery_address')


class OrderItemAdmin(admin.ModelAdmin):
    """Используется для настройки отображения
         и поведения модели позиции заказа в Django Admin."""
    list_display = ('id', 'order', 'offer', 'quantity', 'get_cost')
    list_filter = ('order__status', 'date_added')
    search_fields = ('offer__product',)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
