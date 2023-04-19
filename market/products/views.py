from products.models import Category
from shops.models import Offer
from django.views import generic


class CategoriesListView(generic.ListView):
    """ Представление для отображения меню категорий каталога """
    model = Category
    template_name = 'products/categories.html'
    context_object_name = 'categories'


class ProductsByCategoryView(generic.ListView):
    """ Представление для отображения каталога товаров """
    model = Offer
    template_name = 'products/products.html'
    context_object_name = 'offers'
    paginate_by = 20

    def get_queryset(self):
        self.category = Category.objects.get(id=self.kwargs['pk'])
        queryset = Offer.objects.select_related('shop', 'product').filter(product__category=self.category).order_by(
            '-created')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.category
        return context
