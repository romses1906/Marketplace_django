from django.test import TestCase, Client
from django.urls import reverse

from shops.models import Shop


class ShopDetailViewTest(TestCase):
    """ Тестирование детального представления магазина """
    fixtures = [
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

    def test_view_returns_correct_HTTP_status(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_renders_desired_template(self):
        self.assertTemplateUsed(self.response, "shops/shop_detail.html")
