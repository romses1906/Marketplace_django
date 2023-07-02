import os

from config.settings import FIXTURE_DIRS
from django.db.models import Min, Count, Max, Sum
from django.db.models import Q
from django.shortcuts import get_list_or_404
from django.test import TestCase, Client, override_settings
from django.test import signals
from django.urls import reverse
from jinja2 import Template as Jinja2Template
from products.models import Category, Product
from shops.models import Offer
from users.models import User

ORIGINAL_JINJA2_RENDERER = Jinja2Template.render


def instrumented_render(template_object, *args, **kwargs):
    """ Переопределение метода рендеринга шаблонов Jinja2 """

    context = dict(*args, **kwargs)
    signals.template_rendered.send(
        sender=template_object,
        template=template_object,
        context=context
    )
    return ORIGINAL_JINJA2_RENDERER(template_object, *args, **kwargs)


Jinja2Template.render = instrumented_render


@override_settings(PAGINATE_BY=1000)
class ProductsByCategoryViewTest(TestCase):
    """ Тестирование представления для отображения товаров конкретной категории """

    fixtures = [
        "004_groups.json",
        "005_users.json",
        "010_shops.json",
        "015_categories.json",
        "020_products.json",
        "025_properties.json",
        "030_offers.json",
        "035_products_properties.json",
        "045_reviews_product.json",
        "060_order.json",
        "065_orderitem.json",
    ]

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.get(id=15)
        self.offers = Offer.objects.select_related('shop', 'product__category').filter(product__category=self.category)
        self.url = reverse("products:products_by_category", kwargs={'pk': self.category.pk})
        self.response = self.client.get(self.url)
        self.category_books = Category.objects.get(id=17)
        self.offers_books = Offer.objects.select_related('shop', 'product__category').filter(
            product__category=self.category_books)
        self.url_books = reverse("products:products_by_category", kwargs={'pk': self.category_books.pk})

    def test_view_returns_correct_http_status(self):
        """ Тестирование возврата корректного http-кода при открытии страницы товаров конкретной категории """

        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_desired_template(self):
        """ Тестирование использования ожидаемого шаблона для рендеринга страницы """

        self.assertTemplateUsed(self.response, "products/products.j2")

    def test_products_by_category_count_is_correct(self):
        """ Тестирование количества выводимых товаров, принадлежащих конкретной категории """

        self.assertTrue(len(self.response.context_data['filter'].qs) == self.offers.count())

    def test_products_filtering_by_name(self):
        """ Тестирование корректности фильтрации товаров по названию """

        response = self.client.get(self.url + "?price_min=&price_max=&product_name=лопата#")
        desired_offers = self.offers.filter(product__name__icontains='лопата')
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(product__name__icontains='лопата')
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_price(self):
        """ Тестирование корректности фильтрации товаров по цене """

        response = self.client.get(self.url + "?price_min=300&price_max=600&product_name=#")
        desired_offers = self.offers.filter(price__gte=300, price__lte=600)
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.filter(Q(price__gte=600) | Q(price__lte=300))
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_shop(self):
        """ Тестирование корректности фильтрации товаров по названию магазина """

        response = self.client.get(self.url + "?price_min=&price_max=&product_name=&multiple_shops=1#")
        desired_offers = self.offers.filter(shop__id__in=['1'])
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(shop__id__in=['1'])
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_name_and_price(self):
        """ Тестирование корректности фильтрации товаров по названию товара и цене одновременно """

        response = self.client.get(self.url + "?price_min=400&price_max=600&product_name=лопата#")
        desired_offers = self.offers.filter(price__gte=400, price__lte=600, product__name__icontains='лопата')
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(price__gte=400, price__lte=600, product__name__icontains='лопата')
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_name_and_shop(self):
        """ Тестирование корректности фильтрации товаров по названию товара и названию магазина одновременно """

        response = self.client.get(self.url + "?price_min=&price_max=&product_name=лопата&multiple_shops=1#")
        desired_offers = self.offers.filter(shop__id__in=['1'], product__name__icontains='лопата')
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(shop__id__in=['1'], product__name__icontains='лопата')
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_price_and_shop(self):
        """ Тестирование корректности фильтрации товаров по названию магазина и цене одновременно """

        response = self.client.get(self.url + "?price_min=500&price_max=600&product_name=&multiple_shops=1#")
        desired_offers = self.offers.filter(shop__id__in=['1'], price__gte=500, price__lte=600)
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(shop__id__in=['1'], price__gte=500, price__lte=600)
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_name_and_price_and_shop(self):
        """ Тестирование корректности фильтрации товаров по названию товара, названию магазина и цене одновременно """

        response = self.client.get(self.url + "?price_min=500&price_max=600&product_name=лопата&multiple_shops=1#")
        desired_offers = self.offers.filter(product__name__icontains='лопата', shop__id__in=['1'], price__gte=500,
                                            price__lte=600)
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(product__name__icontains='лопата', shop__id__in=['1'], price__gte=500,
                                               price__lte=600)
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_property_success(self):
        """ Тестирование корректности фильтрации товаров по значению характеристики """

        response = self.client.get(
            self.url + "?price_min=&price_max=&product_name=&multiple_properties=Ручной+инструмент#")
        desired_offers = self.offers.filter(product__product_properties__value__in=['Ручной инструмент'])
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)

    def test_products_filtering_by_property_failure(self):
        """ Тестирование невхождения неподходящих товаров в искомые при фильтрации по значению характеристики """

        response = self.client.get(
            self.url + "?price_min=&price_max=&product_name=&multiple_properties=Ручной+инструмент#")
        undesired_offers = self.offers.exclude(product__product_properties__value__in=['Ручной инструмент'])
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_properties_success(self):
        """ Тестирование корректности фильтрации товаров по значениям нескольких характеристик одновременно """

        response = self.client.get(
            self.url_books + "?price_min=&price_max=&product_name=&multiple_properties=Александр+Сергеевич+Пушкин&"
                             "multiple_properties=Бронислав+Брониславович+Виногродский&multiple_properties=Тонкий&"
                             "multiple_properties=Роман")
        names_properties = {'Автор': {'Александр Сергеевич Пушкин', 'Бронислав Брониславович Виногродский'},
                            'Переплет': {'Тонкий'}, 'Жанр': {'Роман'}}
        for key, value in names_properties.items():
            desired_offers = self.offers_books.select_related('shop', 'product__category').filter(
                product__product_properties__value__in=value).order_by('product__id').distinct(
                'product__id')
        self.assertEqual(len(desired_offers), len(response.context_data['offer_list']))
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)

    def test_products_filtering_by_properties_failure(self):
        """ Тестирование невхождения неподходящих товаров в искомые при фильтрации по
        значениям нескольких характеристик одновременно """

        response = self.client.get(
            self.url_books + "?price_min=&price_max=&product_name=&multiple_properties=Александр+Сергеевич+Пушкин&"
                             "multiple_properties=Бронислав+Брониславович+Виногродский&multiple_properties=Тонкий&"
                             "multiple_properties=Роман")

        names_properties = {'Переплет': {'Твердый'}, 'Жанр': {'Проза', 'Антиутопия', 'Философия'}}
        for key, value in names_properties.items():
            undesired_offers = self.offers_books.select_related('shop', 'product__category').filter(
                product__product_properties__value__in=value).order_by('product__id').distinct(
                'product__id')
        self.assertEqual(len(undesired_offers), len(self.offers_books) - len(response.context_data['offer_list']))
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_properties_and_price_and_name_success(self):
        """ Тестирование корректности фильтрации товаров по значениям нескольких характеристик, цене,
        названию товара одновременно """

        response = self.client.get(
            self.url_books + "?price_min=&price_max=500&product_name=дочка&multiple_properties="
                             "Александр+Сергеевич+Пушкин&multiple_properties=Бронислав+Брониславович+Виногродский&"
                             "multiple_properties=Тонкий&multiple_properties=Роман")
        names_properties = {'Автор': {'Александр Сергеевич Пушкин', 'Бронислав Брониславович Виногродский'},
                            'Переплет': {'Тонкий'}, 'Жанр': {'Роман'}}
        for key, value in names_properties.items():
            desired_offers = self.offers_books.select_related('shop', 'product__category').filter(
                product__name__icontains='дочка', price__lte=500,
                product__product_properties__value__in=value).order_by('product__id').distinct(
                'product__id')
        self.assertEqual(len(desired_offers), len(response.context_data['offer_list']))
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)

    def test_products_filtering_by_properties_and_price_and_name_failure(self):
        """ Тестирование невхождения неподходящих товаров в искомые при фильтрации по значениям нескольких
        характеристик, цене, названию товара одновременно """

        response = self.client.get(
            self.url_books + "?price_min=&price_max=500&product_name=дочка&multiple_properties="
                             "Александр+Сергеевич+Пушкин&multiple_properties=Бронислав+Брониславович+Виногродский&"
                             "multiple_properties=Тонкий&multiple_properties=Роман")
        names_properties = {'Переплет': {'Твердый', 'Тонкий'}, 'Жанр': {'Проза', 'Антиутопия', 'Философия', 'Роман'}}
        for key, value in names_properties.items():
            undesired_offers = self.offers_books.select_related('shop', 'product__category').filter(
                product__product_properties__value__in=value).order_by('product__id').distinct(
                'product__id')
        undesired_offers = undesired_offers.exclude(product__name__icontains='дочка', price__lte=500)
        self.assertEqual(len(undesired_offers), len(self.offers_books) - len(response.context_data['offer_list']))
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_sorting_by_price_is_correct(self):
        """ Тестирование корректности сортировки товаров по цене """

        response = self.client.get(
            self.url_books + "?sort_by=price")
        min_price_of_book = self.offers_books.aggregate(Min('price'))
        first_elem_in_queryset = response.context_data['offer_list'].first()
        second_elem_in_queryset = response.context_data['offer_list'][1]
        self.assertEqual(first_elem_in_queryset.price, min_price_of_book['price__min'])
        self.assertTrue(first_elem_in_queryset.price <= second_elem_in_queryset.price)
        response = self.client.get(
            self.url_books + "?sort_by=-price")
        max_price_of_book = self.offers_books.aggregate(Max('price'))
        first_elem_in_queryset = response.context_data['offer_list'].first()
        second_elem_in_queryset = response.context_data['offer_list'][1]
        self.assertEqual(first_elem_in_queryset.price, max_price_of_book['price__max'])
        self.assertTrue(first_elem_in_queryset.price >= second_elem_in_queryset.price)

    def test_products_sorting_by_created_is_correct(self):
        """ Тестирование корректности сортировки товаров по дате создания """

        response = self.client.get(
            self.url_books + "?sort_by=created")
        old_created_of_book = self.offers_books.aggregate(Min('created'))
        first_elem_in_queryset = response.context_data['offer_list'].first()
        second_elem_in_queryset = response.context_data['offer_list'][1]
        self.assertEqual(first_elem_in_queryset.created, old_created_of_book['created__min'])
        self.assertTrue(first_elem_in_queryset.created <= second_elem_in_queryset.created)
        response = self.client.get(
            self.url_books + "?sort_by=-created")
        new_created_of_book = self.offers_books.aggregate(Max('created'))
        first_elem_in_queryset = response.context_data['offer_list'].first()
        second_elem_in_queryset = response.context_data['offer_list'][1]
        self.assertEqual(first_elem_in_queryset.created, new_created_of_book['created__max'])
        self.assertTrue(first_elem_in_queryset.created >= second_elem_in_queryset.created)

    def test_products_sorting_by_reviews_count_is_correct(self):
        """ Тестирование корректности сортировки товаров по количеству отзывов """

        response = self.client.get(
            self.url_books + "?sort_by=reviews")
        min_reviews_of_book = self.offers_books.annotate(Count('product__product_reviews')).aggregate(
            cnt=Min('product__product_reviews__count'))
        first_elem_in_queryset = response.context_data['offer_list'].first()
        second_elem_in_queryset = response.context_data['offer_list'][1]
        self.assertEqual(first_elem_in_queryset.product.product_reviews.count(), min_reviews_of_book['cnt'])
        self.assertTrue(
            first_elem_in_queryset.product.product_reviews.count() <= second_elem_in_queryset.product.
            product_reviews.count())
        response = self.client.get(
            self.url_books + "?sort_by=-reviews")
        max_reviews_of_book = self.offers_books.annotate(Count('product__product_reviews')).aggregate(
            cnt=Max('product__product_reviews__count'))
        first_elem_in_queryset = response.context_data['offer_list'].first()
        second_elem_in_queryset = response.context_data['offer_list'][1]
        self.assertEqual(first_elem_in_queryset.product.product_reviews.count(), max_reviews_of_book['cnt'])
        self.assertTrue(
            first_elem_in_queryset.product.product_reviews.count() >= second_elem_in_queryset.product.
            product_reviews.count())

    def test_products_sorting_by_popularity_is_correct(self):
        """ Тестирование корректности сортировки товаров по популярности """

        response = self.client.get(
            self.url_books + "?sort_by=popularity")
        min_purchases_of_book = self.offers_books.filter(order__status='paid').annotate(
            Sum('orderitem__quantity')).aggregate(
            cnt=Min('orderitem__quantity__sum'))
        max_purchases_of_book = self.offers_books.filter(order__status='paid').annotate(
            Sum('orderitem__quantity')).aggregate(
            cnt=Max('orderitem__quantity__sum'))

        first_elem_in_queryset_total_purchases = response.context_data['offer_list'].first().total_purchases()
        second_elem_in_queryset_total_purchases = response.context_data['offer_list'][1].total_purchases()
        self.assertEqual(first_elem_in_queryset_total_purchases, min_purchases_of_book['cnt'])
        self.assertTrue(
            first_elem_in_queryset_total_purchases <= second_elem_in_queryset_total_purchases)
        response = self.client.get(
            self.url_books + "?sort_by=-popularity")
        max_purchases_of_book = self.offers_books.filter(order__status='paid').annotate(
            Sum('orderitem__quantity')).aggregate(
            cnt=Max('orderitem__quantity__sum'))
        first_elem_in_queryset_total_purchases = response.context_data['offer_list'].first().total_purchases()
        second_elem_in_queryset_total_purchases = response.context_data['offer_list'][1].total_purchases()
        self.assertEqual(first_elem_in_queryset_total_purchases, max_purchases_of_book['cnt'])
        self.assertTrue(
            first_elem_in_queryset_total_purchases >= second_elem_in_queryset_total_purchases)


class ProductDetailViewTest(TestCase):
    """ Тестирование представления для отображения детальной страницы продукта """

    fixtures = os.listdir(*FIXTURE_DIRS)

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@test.ru', password='test')
        self.client.login(email='test@test.ru', password='test')
        self.product = Product.objects.annotate(
            min_price=Min('offers__price')).annotate(num_reviews=Count('product_reviews')).prefetch_related(
            'product_properties', 'product_images', 'offers', 'product_reviews').get(id=3)
        self.response = self.client.get(self.product.get_absolute_url())

    def test_view_returns_correct_http_status(self):
        """ Тестирование возврата корректного http-кода при открытии детальной страницы товара """

        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_desired_template(self):
        """ Тестирование использования ожидаемого шаблона для рендеринга детальной страницы товара """

        self.assertTemplateUsed(self.response, "products/product.j2")

    def test_context_is_correct(self):
        """ Тестирование корректности передаваемого в шаблон контекста """

        self.assertEqual(self.response.context_data['default_alt'], 'Изображение продукта')
        self.assertEqual(self.response.context_data['categories'], get_list_or_404(Category))
        self.assertEqual(self.response.context_data['product'], self.product)
