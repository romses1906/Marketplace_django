from orders.models import OrderItem, Order


def add_items_from_cart(order: Order, cart):
    cart_items = cart.qs
    order_items = [OrderItem(
        order=order,
        offer=item.offer,
        quantity=item.quantity,
    ) for item in cart_items]
    OrderItem.objects.bulk_create(order_items)
