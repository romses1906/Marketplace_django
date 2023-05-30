from django.db import models
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from shops.models import Offer
from users.models import User


class Order(models.Model):
    """Заказ пользователя сайта."""

    STATUS_CHOICES = (
        ('created', 'Создан'),
        ('paid', 'Оплачено'),
        ('shipped', 'Отправлено'),
        ('delivered', 'Доставлено'),
        ('canceled', 'Отменено'),
    )

    DELIVERY_OPTIONS = (
        ('Delivery', 'Обычная доставка'),
        ('Express Delivery', 'Экспресс-доставка'),
    )

    PAYMENT_OPTIONS = (
        ('Online Card', 'Оналайн картой'),
        ("Another card", 'Оплата чужой картой'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('пользователь'), blank=True)
    full_name = models.CharField(max_length=100, null=True, verbose_name=_('ФИО заказчика'))
    phone_number = PhoneNumberField(unique=True, null=True, region='RU', verbose_name=_('номер телефона'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('создано'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('обнавлено'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name=_('статус'))
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name=_('дата оплаты'))
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_OPTIONS, verbose_name=_('способ доставки'))
    delivery_address = models.CharField(max_length=100, verbose_name=_('адрес доставки'))
    delivery_city = models.CharField(max_length=100, verbose_name=_('город доставки'))
    payment_option = models.CharField(max_length=20, choices=PAYMENT_OPTIONS, verbose_name=_('способ оплаты'))
    comment = models.CharField(max_length=200, verbose_name=_('комментарий'))
    offer = models.ManyToManyField(Offer, through='OrderItem', verbose_name=_('предложение'))

    class Meta:
        verbose_name = _('заказ')
        verbose_name_plural = _('заказы')
        ordering = ('-created',)

    def __str__(self):
        return f'Order {self.id}'

    @property
    def total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def save(self, *args, **kwargs):
        if self.status == 'paid' and not self.payment_date:
            self.payment_date = datetime.now()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Товары размещенные в заказе."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name=_('заказ'), related_name='items')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, verbose_name=_('предложение'))
    quantity = models.PositiveIntegerField(verbose_name=_('количество'))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('дата добавления'))

    class Meta:
        verbose_name = _('позиция заказа')
        verbose_name_plural = _('позиции заказа')
        ordering = ('-date_added',)

    def __str__(self):
        return f'{self.id}'

    def get_cost(self):
        return self.offer.price * self.quantity
