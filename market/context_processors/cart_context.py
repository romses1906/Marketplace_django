from cart.cart import CartServices


def cart(request):
    """Контекстный процессор для
     добавления корзины в контекст шаблонов."""

    cart_len = str(CartServices(request).__len__())
    total_price = str(CartServices(request).get_total_price())
    final_price_with_discount = str(CartServices(request).get_final_price_with_discount())

    return {'cart_len': cart_len, "total_price": total_price, "final_price_with_discount": final_price_with_discount}
