from django.core.validators import MaxValueValidator
from django.db import models
from settings.singleton_model import SingletonModel
from django.utils.translation import gettext_lazy as _

DISCOUNT_VALUE_TYPES = (
    ('percentage', 'Скидка в процентах'),
    ('fixed_amount', 'Фиксированный объем скидки (в рублях)'),
    ('fixed_price', 'Фиксированная цена после применения скидки'),
)


class SiteSettings(SingletonModel):
    """Модель настроек сайта"""

    min_order_price_for_free_shipping = models.DecimalField(
        max_digits=6, decimal_places=2, default=2000.00,
        verbose_name=_(
            'минимальная стоимость заказа для бесплатной доставки, руб'))
    standard_order_price = models.DecimalField(max_digits=6, decimal_places=2, default=200.00,
                                               verbose_name=_('стоимость стандартной досавки, руб'))
    express_order_price = models.DecimalField(max_digits=6, decimal_places=2, default=500.00,
                                              verbose_name=_('стоимость экспресс доставки, руб'))
    banners_count = models.PositiveIntegerField(validators=[MaxValueValidator(3)], default=3,
                                                verbose_name=_('количество баннеров'))
    top_product_count = models.PositiveIntegerField(validators=[MaxValueValidator(8)], default=8,
                                                    verbose_name=_('количество самых популярных товаров'))
    limited_edition_count = models.PositiveIntegerField(validators=[MaxValueValidator(16)], default=16,
                                                        verbose_name=_('количество лимитированных предложений'))
    hot_deals = models.PositiveIntegerField(validators=[MaxValueValidator(9)], default=3,
                                            verbose_name=_('количество горячих предложений'))

    product_cache_time = models.PositiveIntegerField(default=1, verbose_name=_('время кэширования, дней'))

    def __str__(self) -> str:
        return str(_('настройки сайта'))

    class Meta:
        verbose_name_plural = _('настройка')
        verbose_name = _('настройки')


class Discount(models.Model):
    """ Модель скидок на товар """

    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    description = models.TextField(max_length=2048, blank=True, verbose_name=_('описание'))
    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_('дата начала действия скидки'))
    end_date = models.DateTimeField(verbose_name=_('дата окончания действия скидки'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('создана'))
    value = models.IntegerField(verbose_name=_('значение скидки'))
    value_type = models.CharField(max_length=50, choices=DISCOUNT_VALUE_TYPES, verbose_name=_('тип скидки'))
    active = models.BooleanField(default=False, verbose_name=_('активность'))
    products = models.ManyToManyField("products.Product", related_name='discounts', verbose_name=_("продукты"))

    class Meta:
        verbose_name = _('скидка на товар')
        verbose_name_plural = _('скидки на товары')


class DiscountOnCart(models.Model):
    """ Модель скидок на корзину """

    name = models.CharField(max_length=512, verbose_name=_('наименование'))
    description = models.TextField(max_length=2048, blank=True, verbose_name=_('описание'))
    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_('дата начала действия скидки'))
    end_date = models.DateTimeField(verbose_name=_('дата окончания действия скидки'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('создана'))
    value = models.PositiveIntegerField(verbose_name=_('значение скидки'))
    value_type = models.CharField(max_length=50, choices=DISCOUNT_VALUE_TYPES, verbose_name=_('тип скидки'))
    active = models.BooleanField(default=False, verbose_name=_('активность'))
    quantity_at = models.PositiveIntegerField(default=1, verbose_name=_('количество товаров в корзине от'))
    quantity_to = models.PositiveIntegerField(default=1, verbose_name=_('количество товаров в корзине до'))
    cart_total_price_at = models.PositiveIntegerField(default=1,
                                                      verbose_name=_('общая стоимость товаров в корзине от'))

    class Meta:
        verbose_name = _('скидка на корзину')
        verbose_name_plural = _('скидки на корзину')

    def __str__(self):
        return self.name
