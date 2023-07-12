from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q, F
from django.utils.translation import gettext_lazy as _
from settings.singleton_model import SingletonModel

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
    banners_cache_time = models.PositiveIntegerField(default=10, verbose_name=_('время кэширования, минут'))
    top_product_count = models.PositiveIntegerField(validators=[MaxValueValidator(8)], default=8,
                                                    verbose_name=_('количество самых популярных товаров'))
    limited_edition_count = models.PositiveIntegerField(validators=[MaxValueValidator(16)], default=16,
                                                        verbose_name=_('количество лимитированных предложений'))
    hot_deals = models.PositiveIntegerField(validators=[MaxValueValidator(9)], default=3,
                                            verbose_name=_('количество горячих предложений'))

    product_cache_time = models.PositiveIntegerField(default=1, verbose_name=_('время кэширования, дней'))
    categories_cache_time = models.PositiveIntegerField(default=1,
                                                        verbose_name=_('время кэширования меню категорий, дней'))

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
    products = models.ManyToManyField("products.Product", related_name='discounts', verbose_name=_("продукты"))

    class Meta:
        verbose_name = _('скидка на товар')
        verbose_name_plural = _('скидки на товары')
        constraints = (
            CheckConstraint(
                check=Q(end_date__gt=F('start_date')),
                name='check_dates_in_discount',
                violation_error_message='Дата окончания действия скидки должна быть больше даты начала!'
            ),
            CheckConstraint(
                check=Q(value_type__in=('fixed_amount', 'fixed_price')) | (Q(value_type='percentage', value__gt=0) &
                                                                           Q(value_type='percentage', value__lt=100)),
                name='check_value_percentage_in_discount',
                violation_error_message='Процент скидки не может быть менее 0 и более 100'
            ),
        )


class DiscountOnCart(models.Model):
    """ Модель скидок на корзину """

    name = models.CharField(max_length=512, verbose_name=_('наименование'))
    description = models.TextField(max_length=2048, blank=True, verbose_name=_('описание'))
    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_('дата начала действия скидки'))
    end_date = models.DateTimeField(verbose_name=_('дата окончания действия скидки'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('создана'))
    value = models.PositiveIntegerField(verbose_name=_('значение скидки'))
    value_type = models.CharField(max_length=50, choices=DISCOUNT_VALUE_TYPES, verbose_name=_('тип скидки'))
    quantity_at = models.PositiveIntegerField(default=1, verbose_name=_('количество товаров в корзине от'))
    quantity_to = models.PositiveIntegerField(default=1, verbose_name=_('количество товаров в корзине до'))
    cart_total_price_at = models.PositiveIntegerField(default=1,
                                                      verbose_name=_('общая стоимость товаров в корзине от'))

    class Meta:
        verbose_name = _('скидка на корзину')
        verbose_name_plural = _('скидки на корзину')
        constraints = (
            CheckConstraint(
                check=Q(end_date__gt=F('start_date')),
                name='check_dates_in_discount_on_cart',
                violation_error_message='Дата окончания действия скидки должна быть больше даты начала!'
            ),
            CheckConstraint(
                check=Q(value_type__in=('fixed_amount', 'fixed_price')) | (Q(value_type='percentage', value__gt=0) &
                                                                           Q(value_type='percentage', value__lt=100)),
                name='check_value_percentage_in_discount_on_cart',
                violation_error_message='Процент скидки не может быть менее 0 и более 100'
            ),
        )

    def __str__(self):
        return self.name


class DiscountOnSet(models.Model):
    """ Модель скидок на набор товаров """

    name = models.CharField(max_length=512, verbose_name=_('наименование'))
    description = models.TextField(max_length=2048, blank=True, verbose_name=_('описание'))
    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_('дата начала действия скидки'))
    end_date = models.DateTimeField(verbose_name=_('дата окончания действия скидки'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('создана'))
    value = models.PositiveIntegerField(verbose_name=_('значение скидки'))
    value_type = models.CharField(max_length=50, choices=DISCOUNT_VALUE_TYPES, verbose_name=_('тип скидки'))

    class Meta:
        verbose_name = _('скидка на наборы товаров')
        verbose_name_plural = _('скидки на наборы товаров')
        constraints = (
            CheckConstraint(
                check=Q(end_date__gt=F('start_date')),
                name='check_dates_in_discount_on_set',
                violation_error_message='Дата окончания действия скидки должна быть больше даты начала!'
            ),
            CheckConstraint(
                check=Q(value_type__in=('fixed_amount', 'fixed_price')) | (Q(value_type='percentage', value__gt=0) &
                                                                           Q(value_type='percentage', value__lt=100)),
                name='check_value_percentage_in_discount_on_set',
                violation_error_message='Процент скидки не может быть менее 0 и более 100'
            ),
        )

    def __str__(self):
        return self.name


class ProductInDiscountOnSet(models.Model):
    """ Модель товаров из наборов со скидкой """

    product = models.ForeignKey(
        "products.Product", on_delete=models.PROTECT, related_name='products_in_set', verbose_name=_('продукт')
    )
    discount = models.ForeignKey(
        DiscountOnSet, on_delete=models.PROTECT, related_name='products_in_set', verbose_name=_('скидка')
    )

    class Meta:
        verbose_name = _('товар из наборов со скидкой')
        verbose_name_plural = _('товары из наборов со скидкой')
