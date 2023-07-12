from django.conf import settings
from django.core.cache import cache
from django.db.models import Min, Count
from django.shortcuts import get_list_or_404
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django_filters.views import FilterView
from products.filters import ProductFilter
from products.models import Category, Product
from settings.models import SiteSettings
from shops.models import Offer
from viewings.models import HistorySearch, HistorySearchProduct


class ProductsByCategoryView(FilterView):
    """ Представление для отображения каталога товаров """

    template_name = 'products/products.j2'
    filterset_class = ProductFilter

    def get_queryset(self):
        self.category = Category.objects.get(id=self.kwargs['pk'])
        products_cache_time = 60 * 60 * 24 * SiteSettings.load().product_cache_time
        products_by_category = cache.get('products_by_category')
        if not products_by_category:
            products_by_category = Offer.objects.select_related('shop', 'product__category').filter(
                product__category=self.category).order_by(
                '-created')
            cache.set('products_by_category', products_by_category, products_cache_time)
        else:
            actual_products_by_category = Offer.objects.select_related('shop', 'product__category').filter(
                product__category=self.category).order_by(
                '-created')
            if repr(products_by_category) != repr(actual_products_by_category):
                cache.delete('products_by_category')
                products_by_category = actual_products_by_category
                cache.set('products_by_category', products_by_category, products_cache_time)
        return products_by_category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['sorting'] = self.request.GET.get('sort_by')
        return context

    def get_paginate_by(self, queryset):  # переопределяем данный метод, чтобы проходил тест,
        return settings.PAGINATE_BY  # учитывающий пагинацию (общее количество товаров в каталоге)


class ProductDetailView(generic.DetailView):
    """ Представление для отображения детальной страницы продукта """

    template_name = 'products/product.j2'
    context_object_name = 'product'

    def get_queryset(self):
        queryset = Product.objects.annotate(
            min_price=Min('offers__price')).annotate(num_reviews=Count('product_reviews')).prefetch_related(
            'product_properties', 'product_images', 'offers', 'product_reviews')
        if self.request.user.is_authenticated:
            self.add_product_to_user_search_history(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_alt'] = _('Изображение продукта')
        context['categories'] = get_list_or_404(Category)
        context['product_cache_time'] = 60 * 60 * 24 * SiteSettings.load().product_cache_time
        return context

    def add_product_to_user_search_history(self, queryset) -> None:
        """ Добавляет запись в историю просмотра пользователя """

        product_view = queryset.get(pk=self.kwargs['pk'])
        history, create = HistorySearch.objects.get_or_create(user=self.request.user)

        # проверка на содержание таблицы,
        # если запись есть и она не последняя, запись удаляется и становиться последней.
        if HistorySearchProduct.objects.filter(history=history).exists():
            products = HistorySearchProduct.objects.filter(history=history)
            if products.last().product_id != product_view.pk:
                products.filter(product=product_view).delete()
                HistorySearchProduct.objects.create(history=history, product=product_view)
        else:
            HistorySearchProduct.objects.create(history=history, product=product_view)
