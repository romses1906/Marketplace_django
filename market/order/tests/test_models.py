from django.test import TestCase
from django.utils import timezone

from order.models import Order, OrderItem
from users.models import User
from shops.models import Offer, Shop
from products.models import Product, ProductProperty, Property, Category


class OrderModelTest(TestCase):
    """Класс теста моделей заказа и его позиций"""

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
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=90)
        cls.order = Order.objects.create(user=cls.user, status='created', delivery_option='Delivery',
                                         delivery_address='Novgorod', delivery_city='Moscow',
                                         payment_option='Online Card',
                                         comment='Comment 1')
        cls.order_item = OrderItem.objects.create(order=cls.order, offer=cls.offer, quantity=2)

    def test_order_str_method(self):
        """Тестирование функции str для класса Order"""
        expected = f'Order {self.order.id}'
        self.assertEqual(str(self.order), expected)

    def test_order_total_cost_method(self):
        """Тестирование функции total_cost для класса Order"""
        total_cost = sum(item.get_cost() for item in self.order.items.all())
        self.assertEqual(self.order.total_cost, total_cost)

    def test_order_save_method(self):
        """Тестирование установки даты оплаты при изменении
         статуса на paid для класса Order"""
        self.order.status = 'paid'
        self.order.save()
        now = timezone.now()
        self.assertEqual(self.order.payment_date.date(), now.date())

    def test_order_status_change_save_method(self):
        """Тестирование функции save при изменении статуса заказа на 'paid'"""
        self.order.status = "paid"
        self.order.save()
        self.assertIsNotNone(self.order.payment_date)

    def test_order_item_str_method(self):
        """Тестирование функции str для класса OrderItem """
        expected = f'{self.order.items.get().id}'
        self.assertEqual(str(self.order.items.get()), expected)

    def test_order_item_get_cost_method(self):
        """Тестирование функции get_cost для класса OrderItem"""
        expected = self.order_item.offer.price * self.order_item.quantity
        self.assertEqual(self.order_item.get_cost(), expected)
