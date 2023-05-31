from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from products.models import Product
from .comparison import Comparison


class CompareDetail(TemplateView):
    """ Представление для детального отображения страницы сравнения товара """

    template_name = "comparison/compare.j2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compare = Comparison(self.request)
        context["compare"] = compare

        return context


@require_POST
def add_compare_view(request, product_id):
    """ Представление для добавления товаров в список сравнений """

    compare = Comparison(request)
    product = get_object_or_404(Product.objects.select_related("category"),
                                id=product_id)

    compare.add(product)

    return redirect('home')
