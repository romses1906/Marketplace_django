from django.test import TestCase
from django.utils import timezone
from cart.models import Delivery, Order, OrderItem
from users.models import User
from shops.models import Offer, Shop
from products.models import Product, ProductProperty, Property, Category


class OrderModelTest(TestCase):
    """Класс теста моделей заказа и его позиций"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='ivan', email='ivan@mail.ru', password='Password123')
        cls.delivery = Delivery.objects.create(delivery_option='Delivery', order_total_for_free_delivery=2000,
                                               delivery_fee=200)
        cls.property = Property.objects.create(name='Property 1')
        cls.category = Category.objects.create(name='Category 1', description="Description 1")
        cls.product = Product.objects.create(name='Product 1', category=cls.category)
        cls.product.property.add(cls.property)
        ProductProperty.objects.create(product=cls.product, property=cls.property, value=1)
        cls.shop = Shop.objects.create(name='Shop 1', user=cls.user)
        Offer.objects.create(product=cls.product, shop=cls.shop, price=10.0)
        cls.shop.products.add(cls.product)
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=90)
        cls.order = Order.objects.create(user=cls.user, status='created', delivery=cls.delivery,
                                         delivery_address='Novgorod')
        cls.order_item = OrderItem.objects.create(order=cls.order, offer=cls.offer, quantity=2)

    def test_order_str_method(self):
        """Тестирование функция str для класса Order"""
        expected = f'Order {self.order.id}'
        self.assertEqual(str(self.order), expected)

    def test_order_total_cost_method(self):
        """Тестирование функция total_cost для класса Order"""
        total_cost = sum(item.get_cost() for item in self.order.items.all())
        self.assertEqual(self.order.total_cost, total_cost)

    def test_order_save_method(self):
        """Тестирование установки даты оплаты при изменении
         статуса на paid для класса Order"""
        self.order.status = 'paid'
        self.order.save()
        now = timezone.now()
        self.assertEqual(self.order.payment_date.date(), now.date())

    def test_order_item_str_method(self):
        """Тестирование функция str для класса OrderItem """
        expected = f'{self.order.items.get().id}'
        self.assertEqual(str(self.order.items.get()), expected)
