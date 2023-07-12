from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, TemplateView
from products.models import Product
from shops.models import Shop, Banner
from shops.utils import get_offer_of_the_day, get_time_left, get_top_products, hot_deals, limited_edition_products


class ShopDetailView(DetailView):
    """ Отображение детальной страницы продавца """

    model = Shop
    template_name = "shops/shop_detail.j2"
    context_object_name = "shop"


class HomePageView(TemplateView):
    """ Отображение главной страницы сайта """

    template_name = "home.j2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days, hours, minutes, seconds = get_time_left()
        context['banners'] = Banner.objects.get_active_banners()
        context['top_products'] = get_top_products()
        context["offer_of_the_day"] = get_offer_of_the_day()
        context["days"] = days
        context["hours"] = hours
        context["minutes"] = minutes
        context["seconds"] = seconds
        context["hot_deals"] = hot_deals()
        context["limited_edition_products"] = limited_edition_products()
        return context


class SearchView(TemplateView):
    """ Представление для поисковой строки в хэдере """

    template_name = "includes/header/header_search_wrap.j2"

    def post(self, request, *args, **kwargs):
        """ Метод post для обработки запросов поисковой строки в хэдере """

        query = request.POST.get('query')
        products = Product.objects.select_related('category').prefetch_related('property', 'tags').filter(
            name__icontains=query)
        if products:
            category = products.first().category
            redirect_url = reverse('products:products_by_category',
                                   kwargs={'pk': category.id}) + f'?product_name={query}'
            return redirect(redirect_url)
        return redirect('shops:home')
