from django.test import TestCase, Client
from django.urls import reverse, resolve

from shops.models import Shop
from shops.views import ShopDetailView
from users.models import User


class ShopDetailPageTest(TestCase):
    """ Тестирование URL детальной страницы продавца """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@test.ru",
            password="testpassword"
        )
        cls.shop = Shop.objects.create(
            name="test name",
            user=cls.user
        )

    def setUp(self):
        self.client = Client()
        args = [f"{self.shop.id}"]
        self.url = reverse("shops:shop-detail", args=args)
        self.response = self.client.get(self.url)

    def test_page_uses_the_correct_URL(self):
        self.assertURLEqual(self.url, f"/about--seller/{self.shop.id}/")

    def test_URL_uses_the_desired_view(self):
        view = resolve(self.url)
        desired_view = ShopDetailView.as_view().__name__
        self.assertEqual(view.func.__name__, desired_view)
