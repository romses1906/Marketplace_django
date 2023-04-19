from cart.cart import Cart


def cart(request):
    """Контекстный процессор для
     добавления корзины в контекст шаблонов."""
    return {'cart': Cart(request)}
