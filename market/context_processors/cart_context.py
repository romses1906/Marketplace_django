from cart.cart import CartServices


def cart(request):
    """Контекстный процессор для
     добавления корзины в контекст шаблонов."""
    return {'cart': CartServices(request)}
