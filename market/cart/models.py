from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from shops.models import Offer

User = get_user_model()


class Cart(models.Model):
    """Корзина пользователя сайта."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'cart'
        verbose_name = _('корзина')
        verbose_name_plural = _('корзины')

    def __str__(self):
        return f'Cart {self.user}'


class ProductInCart(models.Model):
    """Товары размещенные в корзине."""
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, verbose_name=_('предложение'))
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='products', verbose_name=_('товары'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('количество'))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('дата добавления'))

    class Meta:
        verbose_name = _('позиция в корзине')
        verbose_name_plural = _('позиции в корзине')
        ordering = ('-date_added',)

    def __str__(self):
        return f"Product {self.offer} in cart {self.cart}"

    @property
    def total_price(self):
        return self.quantity * self.offer.price
