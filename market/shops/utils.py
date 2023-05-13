import random
from datetime import datetime, timedelta

from django.db.models import Sum

from shops.models import Offer


def hot_deals():
    """
    Функция возвращает список случайных продуктов на которых действует какая то акция,
     пока в таком виде её надо будет доработать когда появяться акции.
    """
    queryset = Offer.objects.filter(limited_edition=True, in_stock__gte=1)
    num_products = 3
    ids = list(queryset.values_list("product_id", flat=True))
    if len(ids) <= num_products:
        return queryset.select_related("product")
    random_ids = random.sample(ids, k=num_products)
    return queryset.filter(product_id__in=random_ids).select_related("product")


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
    return Offer.objects.annotate(total_quantity=Sum('orderitem__quantity')).order_by('-index', '-total_quantity')[:8]


def limited_edition_products():
    """
    Функция возвращает список товаров ограниченного тиража
    """
    return Offer.objects.filter(limited_edition=True, in_stock__gte=1).exclude(
        id=get_offer_of_the_day().id if get_offer_of_the_day() else -1
    )
