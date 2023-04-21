from products.models import Category
from shops.models import Offer
from django.views import generic
from django_filters.views import FilterView
from products.filters import ProductFilter


class CategoriesListView(generic.ListView):
    """ Представление для отображения меню категорий каталога """
    model = Category
    template_name = 'products/categories.html'
    context_object_name = 'categories'


class ProductsByCategoryView(FilterView):
    """ Представление для отображения каталога товаров """
    model = Offer
    template_name = 'products/products.html'
    paginate_by = 20
    filterset_class = ProductFilter

    def get_queryset(self):
        self.category = Category.objects.get(id=self.kwargs['pk'])
        queryset = Offer.objects.select_related('shop', 'product').filter(product__category=self.category).order_by(
            '-created')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.category
        context['categories'] = Category.objects.all()
        return context
