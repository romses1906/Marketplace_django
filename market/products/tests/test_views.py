from django.test import TestCase, Client
from django.urls import reverse

from products.models import Category


class CategoriesListViewTest(TestCase):
    """ Тестирование представления меню категорий каталога"""
    fixtures = [
        "categories.json",
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
