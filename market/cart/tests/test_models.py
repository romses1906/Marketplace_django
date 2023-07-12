from django.test import TestCase
from django.contrib.auth import get_user_model

from cart.models import Cart, ProductInCart
from shops.models import Offer

User = get_user_model()


class CartModelTest(TestCase):
    """Тестирование модели корзины пользователя."""
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
        cls.offer = Offer.objects.first()
        cls.cart = Cart.objects.create(user=cls.user)

    def test_cart_creation(self):
        """Проверка, на создание корзины для пользователя"""
        self.assertEqual(str(self.cart), f'Cart {self.user}')

    def test_product_in_cart_creation(self):
        """Проверка, на добавление товара в корзину пользователя"""
        ProductInCart.objects.create(
            offer=self.offer, cart=self.cart, quantity=2
        )
        self.assertEqual(self.cart.products.count(), 1)
        product_in_cart = self.cart.products.first()
        self.assertTrue("Лопата штыковая" in str(product_in_cart.offer.product.name))
        self.assertEqual(product_in_cart.quantity, 2)
        self.assertEqual(product_in_cart.total_price, 700)
