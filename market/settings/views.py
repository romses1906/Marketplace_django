from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from settings.models import Discount, DiscountOnCart, DiscountOnSet
from django.conf import settings


def clear_all_cache_view(request):
    """Очистка всего кеша"""
    cache.clear()
    messages.success(request, _('весь кэш удалён'))
    return redirect(request.META.get('HTTP_REFERER'))


class DiscountsListView(ListView):
    """ Отображение страницы скидок """

    context_object_name = "discounts"
    template_name = "sales.j2"
    paginate_by = settings.PAGINATE_BY

    def get_queryset(self):
        discounts = Discount.objects.filter(active=True).values('name', 'description', 'start_date',
                                                                'end_date')
        discounts_on_cart = DiscountOnCart.objects.filter(active=True).values('name', 'description', 'start_date',
                                                                              'end_date')
        discounts_on_set = DiscountOnSet.objects.filter(active=True).values('name', 'description', 'start_date',
                                                                            'end_date')

        return discounts.union(discounts_on_cart, discounts_on_set)
