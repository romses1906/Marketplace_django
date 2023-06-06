from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from settings.models import Discount, DiscountOnCart


def clear_all_cache_view(request):
    """Очистка всего кеша"""
    cache.clear()
    messages.success(request, _('весь кэш удалён'))
    return redirect(request.META.get('HTTP_REFERER'))


class DiscountsListView(ListView):
    """ Отображение страницы скидок """

    context_object_name = "discounts"
    queryset = Discount.objects.filter(active=True)
    template_name = "sales.j2"
    paginate_by = 5  # было 3 и выводит повторно на каждой странице

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['discounts_on_cart'] = DiscountOnCart.objects.filter(active=True)
        return context
