import os

from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from settings.models import Discount, DiscountOnCart, DiscountOnSet


@override_settings(PAGINATE_BY=1000)
class DiscountsListViewTest(TestCase):
    """ Тестирование представления для отображения скидок на товары и скидок на корзину """

    fixtures = os.listdir(*settings.FIXTURE_DIRS)

    def setUp(self):
        self.client = Client()
        self.discounts = Discount.objects.filter(active=True)
        self.discounts_on_cart = DiscountOnCart.objects.filter(active=True)
        self.discounts_on_set = DiscountOnSet.objects.filter(active=True)
        self.url = reverse("settings:sales")
        self.response = self.client.get(self.url)

    def test_view_returns_correct_HTTP_status(self):
        """ Тестирование возврата корректного http-кода при открытии страницы скидок """

        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_desired_template(self):
        """ Тестирование использования ожидаемого шаблона для рендеринга страницы """

        self.assertTemplateUsed(self.response, "sales.j2")

    def test_discounts_count_is_correct(self):
        """ Тестирование количества выводимых скидок """
        self.assertTrue(len(self.response.context_data[
                                'discounts']) == self.discounts.count() + self.discounts_on_cart.count() +
                        self.discounts_on_set.count())
