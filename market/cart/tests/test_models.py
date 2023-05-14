from django.test import TestCase
from django.contrib.auth import get_user_model

from cart.models import Cart, ProductInCart
from products.models import Property, Category, Product, ProductProperty
from shops.models import Shop, Offer

User = get_user_model()


class CartModelTest(TestCase):
    """Тестирование модели корзины пользователя."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='ivan', email='ivan@mail.ru', password='Password123')
        cls.property = Property.objects.create(name='Property 1')
        cls.category = Category.objects.create(name='Category 1', description="Description 1")
        cls.product = Product.objects.create(name='Product 1', category=cls.category)
        cls.product.property.add(cls.property)
        ProductProperty.objects.create(product=cls.product, property=cls.property, value=1)
        cls.shop = Shop.objects.create(name='Shop 1', user=cls.user)
        Offer.objects.create(product=cls.product, shop=cls.shop, price=10.0)
        cls.shop.products.add(cls.product)
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=10)
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
        self.assertTrue("Product 1" in str(product_in_cart))
        self.assertEqual(product_in_cart.total_price, 20)
