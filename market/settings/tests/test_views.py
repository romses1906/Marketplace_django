import os

from config.settings import FIXTURE_DIRS
from django.test import TestCase, Client
from django.urls import reverse
from settings.models import Discount, DiscountOnCart


class DiscountsListViewTest(TestCase):
    """ Тестирование представления для отображения скидок на товары и скидок на корзину """

    fixtures = os.listdir(*FIXTURE_DIRS)

    def setUp(self):
        self.client = Client()
        self.discounts = Discount.objects.filter(active=True)
        self.discounts_on_cart = DiscountOnCart.objects.filter(active=True)
        self.url = reverse("settings:sales")
        self.response = self.client.get(self.url)

    def test_view_returns_correct_HTTP_status(self):
        """ Тестирование возврата корректного http-кода при открытии страницы скидок """

        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_desired_template(self):
        """ Тестирование испоьзования ожидаемого шаблона для рендеринга страницы """

        self.assertTemplateUsed(self.response, "sales.j2")

    def test_discounts_count_is_correct(self):
        """ Тестирование количества выводимых скидок на товары, скидок на корзину товаров """

        self.assertTrue(len(self.response.context_data['discounts']) == self.discounts.count())
        self.assertTrue(len(self.response.context_data['discounts_on_cart']) == self.discounts_on_cart.count())
