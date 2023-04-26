import os

from django.db.models import Min, Count
from django.shortcuts import get_list_or_404
from django.test import TestCase, Client
from django.urls import reverse
from django.db.models import Q

from config.settings import FIXTURE_DIRS
from products.models import Category, Product
from shops.models import Offer


class CategoriesListViewTest(TestCase):
    """ Тестирование представления меню категорий каталога"""

    fixtures = [
        "015_categories.json",
    ]

    def setUp(self):
        self.client = Client()
        self.categories = Category.objects.all()
        url = reverse("products:categories_list")
        self.response = self.client.get(url)

    def test_view_returns_correct_HTTP_status(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_desired_template(self):
        self.assertTemplateUsed(self.response, "products/categories.html")

    def test_categories_count_is_correct(self):
        self.assertTrue(len(self.response.context['categories']) == self.categories.count())


class ProductsByCategoryViewTest(TestCase):
    """ Тестирование представления для отображения товаров конкретной категории """

    fixtures = [
        "004_groups.json",
        "005_users.json",
        "010_shops.json",
        "015_categories.json",
        "020_products.json",
        "030_offers.json",
    ]

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.get(id=15)
        self.offers = Offer.objects.select_related('shop', 'product').filter(product__category=self.category)
        self.url = reverse("products:products_by_category", kwargs={'pk': self.category.pk})
        self.response = self.client.get(self.url)

    def test_view_returns_correct_HTTP_status(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_desired_template(self):
        self.assertTemplateUsed(self.response, "products/products.html")

    def test_products_by_category_count_is_correct(self):
        self.assertTrue(len(self.response.context['offer_list']) == self.offers.count())
        self.assertTrue(len(self.response.context['filter'].qs) == self.offers.count())

    def test_products_filtering_by_name(self):
        response = self.client.get(self.url + "?price_min=&price_max=&product_name=лопата#")
        desired_offers = self.offers.filter(product__name__icontains='лопата')
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(product__name__icontains='лопата')
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_price(self):
        response = self.client.get(self.url + "?price_min=300&price_max=600&product_name=#")
        desired_offers = self.offers.filter(price__gte=300, price__lte=600)
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.filter(Q(price__gte=600) | Q(price__lte=300))
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_shop(self):
        response = self.client.get(self.url + "?price_min=&price_max=&product_name=&multiple_shops=1#")
        desired_offers = self.offers.filter(shop__id__in=['1'])
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(shop__id__in=['1'])
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_name_and_price(self):
        response = self.client.get(self.url + "?price_min=400&price_max=600&product_name=лопата#")
        desired_offers = self.offers.filter(price__gte=400, price__lte=600, product__name__icontains='лопата')
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(price__gte=400, price__lte=600, product__name__icontains='лопата')
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_name_and_shop(self):
        response = self.client.get(self.url + "?price_min=&price_max=&product_name=лопата&multiple_shops=1#")
        desired_offers = self.offers.filter(shop__id__in=['1'], product__name__icontains='лопата')
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(shop__id__in=['1'], product__name__icontains='лопата')
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_price_and_shop(self):
        response = self.client.get(self.url + "?price_min=500&price_max=600&product_name=&multiple_shops=1#")
        desired_offers = self.offers.filter(shop__id__in=['1'], price__gte=500, price__lte=600)
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(shop__id__in=['1'], price__gte=500, price__lte=600)
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)

    def test_products_filtering_by_name_and_price_and_shop(self):
        response = self.client.get(self.url + "?price_min=500&price_max=600&product_name=лопата&multiple_shops=1#")
        desired_offers = self.offers.filter(product__name__icontains='лопата', shop__id__in=['1'], price__gte=500,
                                            price__lte=600)
        for offer in desired_offers:
            self.assertContains(response, offer.product.name)
        undesired_offers = self.offers.exclude(product__name__icontains='лопата', shop__id__in=['1'], price__gte=500,
                                               price__lte=600)
        for offer in undesired_offers:
            self.assertNotContains(response, offer.product.name)


class ProductDetailViewTest(TestCase):
    """ Тестирование представления для отображения детальной страницы продукта """
    fixtures = os.listdir(*FIXTURE_DIRS)

    def setUp(self):
        self.client = Client()
        self.product = Product.objects.annotate(
            min_price=Min('offers__price')).annotate(num_reviews=Count('offers__reviews')).prefetch_related(
            'product_properties', 'product_images', 'offers', 'offers__reviews').get(id=6)
        self.response = self.client.get(self.product.get_absolute_url())

    def test_view_returns_correct_HTTP_status(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_desired_template(self):
        self.assertTemplateUsed(self.response, "products/product.html")

    def test_context_is_correct(self):
        self.assertEqual(self.response.context['default_alt'], 'Изображение продукта')
        self.assertEqual(self.response.context['categories'], get_list_or_404(Category))
        self.assertEqual(self.response.context['product'], self.product)
