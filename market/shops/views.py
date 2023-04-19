from django.views import generic

from .models import Shop


class ShopDetailView(generic.DetailView):
    """ Отображение детальной страницы продавца """
    model = Shop
    context_object_name = "shop"


class T(generic.TemplateView):
    template_name = "base.jinja"
