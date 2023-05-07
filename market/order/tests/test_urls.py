from django.test import TestCase, Client
from django.urls import reverse_lazy

from order.models import Order
from users.models import User


class CartUrlsTest(TestCase):
    """Тестирование URL пошагового оформления заказа."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test@test.ru', email='test@test.ru', password='2304test')
        cls.client = Client()
        cls.order = Order.objects.create(user=cls.user, status='created', delivery_option='Delivery',
                                         delivery_address='Novgorod', delivery_city='Moscow',
                                         payment_option='Online Card',
                                         comment='Comment 1')

    def test_url_step1_view(self):
        """Тестирование URL первого шага оформления заказа."""
        self.client.login(username='test@test.ru', password='2304test')
        response = self.client.get(reverse_lazy('order:step1'))
        self.assertEqual(response.status_code, 200)

    def test_url_step2_view(self):
        """Тестирование URL второго шага оформления заказа."""
        self.client.login(username='test@test.ru', password='2304test')
        response = self.client.get(reverse_lazy('order:step2'))
        self.assertEqual(response.status_code, 200)

    def test_url_step3_view(self):
        """Тестирование URL третьего шага оформления заказа."""
        self.client.login(username='test@test.ru', password='2304test')
        response = self.client.get(reverse_lazy('order:step3'))
        self.assertEqual(response.status_code, 200)

    def test_url_step4_view(self):
        """Тестирование URL четвертого шага оформления заказа."""
        self.client.login(username='test@test.ru', password='2304test')
        response = self.client.get(reverse_lazy('order:step4'))
        self.assertEqual(response.status_code, 200)

    def test_url_detail_order_view(self):
        """Тестирование URL детального отображения заказа."""
        self.client.login(username='test@test.ru', password='2304test')
        order = Order.objects.first()
        response = self.client.get(reverse_lazy('order:detail_order', kwargs={'pk': order.id}))
        self.assertEqual(response.status_code, 200)

    def test_url_history_view(self):
        """Тестирование URL отображения истории заказов."""
        self.client.login(username='test@test.ru', password='2304test')
        response = self.client.get(reverse_lazy('order:history'))
        self.assertEqual(response.status_code, 200)
