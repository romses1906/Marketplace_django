from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse

from users.models import User
from shops.models import Shop, Offer
from products.models import Product, Property, ProductProperty, Category
from cart.models import Cart, ProductInCart
from cart.cart import CartServices


class CartViewTest(TestCase):
    """Тестирование представлений корзины пользователя."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='ivan@mail.ru', email='ivan@mail.ru', password='TestPassword123')
        cls.property = Property.objects.create(name='Property 1')
        cls.category = Category.objects.create(name='Category 1', description="Description 1")
        cls.product = Product.objects.create(name='Product 1', category=cls.category)
        ProductProperty.objects.create(product=cls.product, property=cls.property, value=1)
        cls.product.property.add(cls.property)
        cls.shop = Shop.objects.create(name='Shop 1', user=cls.user)
        Offer.objects.create(product=cls.product, shop=cls.shop, price=10.0)
        cls.shop.products.add(cls.product)
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=100, in_stock=10)
        cls.session = {}
        cls.client = Client()
        cls.request = cls.client.request().wsgi_request
        cls.request.session.update(cls.session)
        cls.cart = CartServices(cls.request)
        cls.cart.update(cls.offer, 1)
        cls.url = reverse('cart:cart')

    def test_cart_view_context(self):

        response = self.client.get(self.url)
        cartmodel = Cart.objects.all()
        print("cartmodel", cartmodel)
        cart_items = response.context['cart_items']
        print(cart_items)
        cart_total_price = response.context['cart_total_price']
        if cart_items:
            self.assertEqual(cart_items.get_total_items(), len(cart_items))
            self.assertEqual(cart_total_price, cart_items.get_total_price())
        else:
            self.assertEqual(cart_total_price, Decimal('0'))

    def test_cart_view(self):
        # Переход на страницу корзины
        response = self.client.get(self.url)
        print(response.context)
        self.assertEqual(response.status_code, 200)
        # Проверка отображения содержимого корзины
        self.assertContains(response, 'Product 1')
        self.assertContains(response, '100.00')
        self.assertContains(response, '1')
        self.assertContains(response, '100.00')

        # Проверка сохранения корзины в базу данных
        self.assertEqual(Cart.objects.filter(user=self.user, is_active=True).count(), 1)
        self.assertEqual(ProductInCart.objects.filter(cart__user=self.user).count(), 1)

        self.assertEqual(self.cart.get_total_price(), 100.00)

    def test_update_cart_view(self):
        url = reverse('cart:update_to_cart')
        response = self.client.post(url, {
            'product_id': self.offer.id,
            'quantity': 1
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'product_id': str(self.offer.id),
            'product_quantity': '1',
            'product_total_price': '100.00',
            'cart_total_price': '100.00'
        })

    def test_remove_from_cart_view(self):
        url = reverse('cart:remove_from_cart', kwargs={'product_id': self.offer.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('cart:cart'))
        self.assertEqual(Cart.objects.filter(user=self.user, is_active=True).count(), 0)
