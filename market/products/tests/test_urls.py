from django.test import TestCase, Client
from django.urls import reverse, resolve

from products.views import CategoriesListView


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
