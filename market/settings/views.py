from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from settings.models import Discount, DiscountOnCart, DiscountOnSet


def clear_all_cache_view(request):
    """Очистка всего кеша"""
    cache.clear()
    messages.success(request, _('весь кэш удалён'))
    return redirect(request.META.get('HTTP_REFERER'))


class DiscountsListView(ListView):
    """ Отображение страницы скидок """

    context_object_name = "discounts"
    template_name = "sales.j2"

    def get_queryset(self):
        date_now = datetime.now(tz=timezone.utc)
        discounts = Discount.objects.filter(end_date__gte=date_now).values('name', 'description', 'start_date',
                                                                           'end_date')
        discounts_on_cart = DiscountOnCart.objects.filter(end_date__gte=date_now).values('name', 'description',
                                                                                         'start_date',
                                                                                         'end_date')
        discounts_on_set = DiscountOnSet.objects.filter(end_date__gte=date_now).values('name', 'description',
                                                                                       'start_date',
                                                                                       'end_date')

        return discounts.union(discounts_on_cart, discounts_on_set)

    def get_paginate_by(self, queryset):  # переопределяем данный метод, чтобы проходил тест,
        return settings.PAGINATE_BY  # учитывающий пагинацию (общее количество скидок)
