from django.test import TestCase, Client
from django.urls import reverse

from cart.models import User
from shops.models import Offer


class CartURLTestCase(TestCase):
    """Тестирование URL корзины пользователя."""
    fixtures = [
        "004_groups.json",
        "005_users.json",
        "010_shops.json",
        "015_categories.json",
        "020_products.json",
        "030_offers.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='ivan', email='ivan@mail.ru', password='Password123')
        cls.session = {}
        cls.client = Client()
        cls.offer = Offer.objects.first()
        cls.cart_url = reverse('cart:cart')
        cls.update_url = reverse('cart:update_to_cart')
        cls.remove_url = reverse('cart:remove_from_cart', args=[cls.offer.pk])

    def test_cart_view_url(self):
        """Тестирование URL представления отображения корзины."""
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)

    def test_update_cart_view_post_request(self):
        """Тестирование URL представления обнавления количества товара в корзине."""
        data = {
            'product_id': self.offer.pk,
            'quantity': 2
        }
        response = self.client.post(self.update_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.client.session.get('cart')), 1)

    def test_remove_from_cart_view_removes_from_cart(self):
        """Тестирование URL представления удаления количества товара в корзине."""
        data = {
            'product_id': self.offer.pk,
            'quantity': 2
        }
        self.client.post(self.update_url, data=data)
        self.assertEqual(len(self.client.session.get('cart')), 1)
        response = self.client.get(self.remove_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(self.client.session.get('cart')), 0)
