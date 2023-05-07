from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.test import TestCase, Client

from cart.cart import CartServices
from cart.models import Cart, ProductInCart
from shops.models import Offer, Shop
from products.models import Product, Property, Category, ProductProperty
from order.models import Order, OrderItem
from users.models import User


class Step4ViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser', email='ivan@mail.ru', password='TestPassword123')
        cls.property = Property.objects.create(name='Property 1')
        cls.category = Category.objects.create(name='Category 1', description="Description 1")
        cls.product = Product.objects.create(name='Product 1', category=cls.category)
        ProductProperty.objects.create(product=cls.product, property=cls.property, value=1)
        cls.product.property.add(cls.property)
        cls.shop = Shop.objects.create(name='Shop 1', user=cls.user)
        Offer.objects.create(product=cls.product, shop=cls.shop, price=10.0)
        cls.shop.products.add(cls.product)
        cls.offer1 = Offer.objects.create(shop=cls.shop, product=cls.product, price=100, in_stock=10)
        cls.offer2 = Offer.objects.create(shop=cls.shop, product=cls.product, price=200, in_stock=10)
        cls.session = {}
        cls.client = Client()
        cls.request = cls.client.request().wsgi_request
        cls.request.session.update(cls.session)
        cls.cart = Cart.objects.create(user=cls.user, is_active=True)
        cls.product1 = ProductInCart.objects.create(offer=cls.offer1, cart=cls.cart, quantity=1)
        cls.product2 = ProductInCart.objects.create(offer=cls.offer2, cart=cls.cart, quantity=2)
        cls.client.login(username='testuser', password='TestPassword123')
        cls.url = reverse('order:step4')

    def test_step4_view(self):
        post_data = {
            "full_name": "Ivanov Ivna Ivanovich",
            "delivery_option": "Delivery",
            "delivery_address": "Mira, 1",
            "delivery_city": "Minsk",
            "payment_option": "Online Card",
            "comment": "comment",
        }

        response = self.client.post(reverse_lazy('order:step4'), data=post_data)

        self.assertEqual(response.status_code, 302)

        print("response", response)

