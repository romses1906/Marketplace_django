from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _


def clear_all_cache_view(request):
    """Очистка всего кеша"""
    cache.clear()
    messages.success(request, _('весь кэш удалён'))
    return redirect(request.META.get('HTTP_REFERER'))
