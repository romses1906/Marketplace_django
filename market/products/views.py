from account.models import HistorySearch, HistorySearchProduct
from django.conf import settings
from django.db.models import Min, Count
from django.shortcuts import get_list_or_404
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django_filters.views import FilterView
from products.filters import ProductFilter
from products.models import Category, Product
from shops.models import Offer


class ProductsByCategoryView(FilterView):
    """ Представление для отображения каталога товаров """

    template_name = 'products/products.j2'
    filterset_class = ProductFilter

    def get_queryset(self):
        self.category = Category.objects.get(id=self.kwargs['pk'])
        queryset = Offer.objects.select_related('shop', 'product__category').filter(
            product__category=self.category).order_by(
            '-created')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['sorting'] = self.request.GET.get('sort_by')
        return context

    def get_paginate_by(self, queryset):  # переопределяем данный метод, чтобы проходил тест,
        return settings.PAGINATE_BY  # учитывающий пагинацию (общее количество товаров в каталоге)


class ProductDetailView(generic.DetailView):
    """ Представление для отображения детальной страницы продукта """
    template_name = 'products/product.html'
    context_object_name = 'product'

    def get_queryset(self):
        queryset = Product.objects.annotate(
            min_price=Min('offers__price')).annotate(num_reviews=Count('product_reviews')).prefetch_related(
            'product_properties', 'product_images', 'offers', 'product_reviews')
        self.add_product_to_user_search_history(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_alt'] = _('Изображение продукта')
        context['categories'] = get_list_or_404(Category)
        return context

    def add_product_to_user_search_history(self, queryset) -> None:
        """ Добавляет запись в историю просмотра пользователя """
        history, create = HistorySearch.objects.get_or_create(user=self.request.user)
        HistorySearchProduct.objects.create(history=history, product=queryset.get(pk=self.kwargs['pk']))
