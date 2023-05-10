from django.test import TestCase, Client
from django.urls import reverse

from cart.models import User
from products.models import Property, Category, Product, ProductProperty
from shops.models import Offer, Shop


class CartURLTestCase(TestCase):
    """Тестирование URL корзины пользователя."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='ivan', email='ivan@mail.ru', password='Password123')
        cls.property = Property.objects.create(name='Property')
        cls.category = Category.objects.create(name='Category', description="Description 1")
        cls.product = Product.objects.create(name='Product', category=cls.category)
        ProductProperty.objects.create(product=cls.product, property=cls.property, value=1)
        cls.product.property.add(cls.property)
        cls.shop = Shop.objects.create(name='Shop 1', user=cls.user)
        Offer.objects.create(product=cls.product, shop=cls.shop, price=10.0)
        cls.shop.products.add(cls.product)
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=100, in_stock=10)
        cls.session = {}
        cls.client = Client()
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
