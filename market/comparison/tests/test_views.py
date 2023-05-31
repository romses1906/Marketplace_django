import os

from django.test import TestCase, Client
from django.urls import reverse
from jinja2 import Template as Jinja2Template

from comparison.comparison import Comparison
from config.settings import FIXTURE_DIRS
from products.models import Product
from products.tests.test_views import instrumented_render

Jinja2Template.render = instrumented_render


class CompareDetailTest(TestCase):
    """ Класс тестирования представления детальной страницы сравнения """

    def setUp(self):
        url = reverse("comparison:compare-detail")
        self.response = self.client.get(url)

    def test_view_returns_correct_http_status(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_desired_template(self):
        self.assertTemplateUsed(self.response, "comparison/compare.j2")

    def test_compare_detail_context(self):
        compare = self.response.context
        self.assertIn("compare", compare)
        self.assertIsInstance(compare["compare"], Comparison)


class AddCompareViewTest(TestCase):
    """ Класс тестирования представления для добавления в список сравнения. """

    fixtures = os.listdir(*FIXTURE_DIRS)

    def setUp(self):
        self.product = Product.objects.get(id=1)
        self.url = reverse("comparison:add-to-compare",
                           kwargs={"product_id": self.product.pk})
        self.client = Client()
        self.response = self.client.post(self.url)

    def test_view_uses_redirect(self):
        redirect_url = reverse("home")
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, redirect_url)

    def test_view_adds_product_to_compare(self):
        compare = Comparison(self.client)
        compare.add(self.product)

        category_id = str(self.product.category_id)
        category_name = str(self.product.category)
        product_id = str(self.product.id)
        check_dict = {category_id: [category_name, {product_id: {}}]}

        self.assertDictEqual(compare.compare, check_dict)
