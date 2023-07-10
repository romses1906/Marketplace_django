from datetime import datetime
from decimal import Decimal

from django.apps import apps
from django.core.cache import cache
from django.utils import timezone
from settings.models import Discount, SiteSettings


class BannerService:
    """Сервис для получения и кэширования активных баннеров."""

    @staticmethod
    def get_active_banners():
        banners_cache_time = 60 * SiteSettings.load().banners_cache_time
        Banner = apps.get_model('shops', 'Banner')
        banners = cache.get('active_banners')

        if not banners:
            banners = list(Banner.objects.filter(is_active=True).order_by('?')[:3])
            cache.set('active_banners', banners, banners_cache_time)
        else:
            active_banners = list(Banner.objects.filter(is_active=True).order_by('?')[:3])
            if banners != active_banners:
                cache.delete('active_banners')
                banners = active_banners
                cache.set('active_banners', banners, banners_cache_time)

        return banners


def offer_price_with_discount(product_id: int, price: Decimal) -> Decimal:
    """
    Функция возвращает цену товара со скидкой
    """

    date_now = datetime.now(tz=timezone.utc)
    discounts = Discount.objects.filter(products__id=product_id, end_date__gte=date_now)
    if discounts:
        disc_prices_lst = []
        for discount in discounts:
            disc_price = 0
            if discount.value_type == 'percentage':
                disc_price = price * Decimal((1 - discount.value / 100))
            elif discount.value_type == 'fixed_amount':
                disc_price = price - discount.value
            elif discount.value_type == 'fixed_price':
                disc_price = discount.value
            if disc_price > 0:
                disc_prices_lst.append(disc_price)
            else:
                disc_prices_lst.append(1)
        disc_price = min(disc_prices_lst)
        return Decimal(disc_price).quantize(Decimal('1.00'))
