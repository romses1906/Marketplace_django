from products.models import Category
from django.views import generic


class CategoriesListView(generic.ListView):
    """ Представление для отображения меню категорий каталога """
    model = Category
    template_name = 'products/categories.html'
    context_object_name = 'categories'
