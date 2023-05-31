import re

from order.models import OrderItem, Order


def add_items_from_cart(order: Order, cart):
    cart_items = cart.qs
    order_items = [OrderItem(
        order=order,
        offer=item.offer,
        quantity=item.quantity,
    ) for item in cart_items]
    OrderItem.objects.bulk_create(order_items)


def format_number(phone_number):
    digits = re.sub(r'\D+', '', phone_number)
    phone = "+7 ({}) {}-{}-{}".format(digits[1:4], digits[4:7], digits[7:9], digits[9:11])
    return phone
