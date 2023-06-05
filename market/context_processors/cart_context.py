from cart.cart import CartServices


def cart(request):
    """Контекстный процессор для
     добавления корзины в контекст шаблонов."""

    cart_len = str(CartServices(request).__len__())
    total_price = str(CartServices(request).get_total_price())
    return {'cart_len': cart_len, "total_price": total_price}
