from django.test import TestCase, Client
from django.urls import reverse, resolve

from products.views import CategoriesListView, ProductsByCategoryView, ProductDetailView
from products.models import Category, Product


class CategoriesListPageTest(TestCase):
    """ Тестирование URL меню категорий каталога """

    def setUp(self):
        self.client = Client()
        self.url = reverse("products:categories_list")
        self.response = self.client.get(self.url)

    def test_page_uses_the_correct_URL(self):
        self.assertURLEqual(self.url, "/catalog/")

    def test_URL_uses_the_desired_view(self):
        view = resolve(self.url)
        desired_view = CategoriesListView.as_view().__name__
        self.assertEqual(view.func.__name__, desired_view)


class ProductsByCategoryPageTest(TestCase):
    """ Тестирование URL товаров конкретной категории """

    fixtures = [
        "004_groups.json",
        "005_users.json",
        "015_categories.json",
        "020_products.json",
        "010_shops.json",
        "030_offers.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.get(id=17)
        cls.client = Client()
        cls.url = reverse("products:products_by_category", kwargs={'pk': cls.category.pk})
        cls.response = cls.client.get(cls.url)

    def test_page_uses_the_correct_URL(self):
        category_pk = self.category.pk
        self.assertURLEqual(self.url, f"/catalog/{category_pk}/")

    def test_URL_uses_the_desired_view(self):
        view = resolve(self.url)
        desired_view = ProductsByCategoryView.as_view().__name__
        self.assertEqual(view.func.__name__, desired_view)


class ProductDetailPageTest(TestCase):
    """ Тестирование URL детальной страницы продукта """

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.product = Product.objects.create(name='тестовый продукт', category=cls.category)
        cls.url = reverse("products:product_detail", kwargs={'pk': cls.product.pk})
        cls.response = cls.client.get(cls.url)

    def test_page_uses_the_correct_URL(self):
        self.assertURLEqual(self.url, f"/catalog/item/{self.product.pk}/")

    def test_URL_uses_the_desired_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, ProductDetailView.as_view().__name__)
