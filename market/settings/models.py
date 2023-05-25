from django.core.validators import MaxValueValidator
from django.db import models
from settings.singleton_model import SingletonModel
from django.utils.translation import gettext_lazy as _


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
