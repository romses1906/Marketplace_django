import random
from datetime import datetime, timedelta

from django.db.models import Sum
from settings.models import SiteSettings, Discount, DiscountOnSet
from shops.models import Offer


def hot_deals():
    """
    Функция возвращает список продуктов на которых действует какая-то акция.
    """
    now = datetime.now()
    discounts = Discount.objects.filter(end_date__gte=now)
    discount_products = []
    for discount in discounts:
        discount_products += list(discount.products.all())
    discount_sets = DiscountOnSet.objects.filter(end_date__gte=now).prefetch_related('products_in_set')
    for discount_set in discount_sets:
        discount_products += [p.product for p in discount_set.products_in_set.all()]
    discount_queryset = Offer.objects.filter(in_stock__gte=1, product__in=discount_products)
    num_products = SiteSettings.load().hot_deals
    ids = list(discount_queryset.values_list("id", flat=True))
    if len(ids) <= num_products:
        return discount_queryset
    random_ids = random.sample(ids, k=num_products)
    return discount_queryset.filter(id__in=random_ids)


def get_time_left():
    """
    Функция возвращает дни, часы, минуты и секунды оставшиеся до конца текущего дня.
    """
    end_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    time_left = end_of_day - datetime.now()
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return days, hours, minutes, seconds


def get_offer_of_the_day():
    """
    Функция возвращает предложение текущего дня.
    """
    today = datetime.now().date()
    offer_of_the_day = Offer.objects.filter(created__date=today, limited_edition=True, in_stock__gte=1).first()
    if not offer_of_the_day:
        offer_of_the_day = Offer.objects.filter(limited_edition=True, in_stock__gte=1).order_by('?').first()
        if offer_of_the_day:
            offer_of_the_day.is_offer_of_the_day = True
            offer_of_the_day.created = today
            offer_of_the_day.save()
    return offer_of_the_day


def get_top_products():
    """
    Функция возвращает список 8 саммых популярных товаров
    """
    count = SiteSettings.load().top_product_count
    return Offer.objects.annotate(
        total_quantity=Sum('orderitem__quantity')).order_by('-index', '-total_quantity')[:count]


def limited_edition_products():
    """
    Функция возвращает список товаров ограниченного тиража
    """
    count = SiteSettings.load().limited_edition_count
    return Offer.objects.filter(limited_edition=True, in_stock__gte=1).exclude(
        id=get_offer_of_the_day().id if get_offer_of_the_day() else -1
    )[:count]
