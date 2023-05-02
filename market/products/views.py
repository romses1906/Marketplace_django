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
    paginate_by = 6
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
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(generic.DetailView):
    """ Представление для отображения детальной страницы продукта """
    template_name = 'products/product.html'
    context_object_name = 'product'

    def get_queryset(self):
        queryset = Product.objects.annotate(
            min_price=Min('offers__price')).annotate(num_reviews=Count('product_reviews')).prefetch_related(
            'product_properties', 'product_images', 'offers', 'product_reviews')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_alt'] = _('Изображение продукта')
        context['categories'] = get_list_or_404(Category)
        return context
