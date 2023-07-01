import os

from django.test import TestCase, Client
from django.urls import reverse

from config.settings import FIXTURE_DIRS
from order.models import OrderItem
from shops.models import Shop, Banner, Offer
from shops.utils import get_time_left


class ShopDetailViewTest(TestCase):
    """ Тестирование детального представления магазина """

    fixtures = [
        "004_groups.json",
        "005_users.json",
        "010_shops.json"
    ]

    def setUp(self):
        self.client = Client()
        self.shop = Shop.objects.get(id=1)
        kwargs = {
            "pk": self.shop.pk,
        }
        url = reverse("shops:shop-detail", kwargs=kwargs)
        self.response = self.client.get(url)

    def test_view_returns_correct_http_status(self):
        """ Тестирование возврата корректного http-кода при открытии детальной страницы магазина """

        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_desired_template(self):
        """ Тестирование использования ожидаемого шаблона для рендеринга страницы """

        self.assertTemplateUsed(self.response, "shops/shop_detail.j2")


class TestHomePageView(TestCase):
    """ Тестирование главной страницы магазина """
    fixtures = os.listdir(*FIXTURE_DIRS)

    def setUp(self):
        self.client = Client()

    def test_homepage_view(self):
        """ Тест главной страницы магазина """

        url = reverse('shops:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        days, hours, minutes, seconds = get_time_left()
        self.assertEqual(response.context_data['days'], days)
        self.assertEqual(response.context_data['hours'], hours)
        self.assertEqual(response.context_data['minutes'], minutes)
        self.assertTrue(all(isinstance(banner, Banner) for banner in response.context_data['banners']))
        self.assertTrue(len(response.context_data['top_products']) <= 8)
        self.assertTrue(len(response.context_data['hot_deals']) <= 3)
        self.assertTrue(response.context_data['limited_edition_products'].exists())

        offer_of_the_day = response.context_data['offer_of_the_day']
        if offer_of_the_day:
            self.assertIsInstance(offer_of_the_day, Offer)
            self.assertTrue(offer_of_the_day.limited_edition)
            self.assertContains(response, offer_of_the_day.product.name)

        hot_deals_offers = response.context_data['hot_deals']
        order_items = OrderItem.objects.filter(offer__in=hot_deals_offers)
        total_quantity = 0
        for order_item in order_items:
            total_quantity += order_item.quantity
        # self.assertGreater(total_quantity, 0)
