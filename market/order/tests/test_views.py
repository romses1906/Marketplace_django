from django.test import TestCase, Client
from django.urls import reverse

from order.models import Order
from users.models import User


class TestOrderViews(TestCase):
    """
    Тест представлений оформления заказа
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test@test.ru', email='test@test.ru', password='2304test')
        cls.client = Client()
        cls.client.login(username='test@test.ru', password='2304test')

        cls.user_data = {'full_name': 'Ivan Ivanovich Ivanov',
                         'email': 'ivan@mail.ru',
                         'phone_number': '+79072223340'}
        cls.shipping_data = {'delivery_option': 'Delivery',
                             'delivery_address': '123 Main St',
                             'delivery_city': 'New York'}
        cls.payment_data = {'payment_option': 'Online Card'}

        cls.order = Order.objects.create(user=cls.user, status='created', delivery_option='Delivery',
                                         delivery_address='Novgorod', delivery_city='Moscow',
                                         payment_option='Online Card',
                                         comment='Comment 1')

    def test_step1_view(self):
        self.client.login(username='test@test.ru', password='2304test')
        response = self.client.get(reverse('order:step1'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('order:step1'), data=self.user_data)
        self.assertRedirects(response, reverse('order:step2'))

    def test_step2_view(self):
        self.client.login(username='test@test.ru', password='2304test')
        response = self.client.get(reverse('order:step2'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('order:step2'), data=self.shipping_data)
        self.assertRedirects(response, reverse('order:step3'))

    def test_step3_view(self):
        self.client.login(username='test@test.ru', password='2304test')
        response = self.client.get(reverse('order:step3'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('order:step3'), data=self.payment_data)
        self.assertRedirects(response, reverse('order:step4'))

    def test_order_detail_view(self):
        self.client.login(username='test@test.ru', password='2304test')
        order = Order.objects.first()
        url = reverse('order:detail_order', kwargs={'pk': order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_order_list_view(self):
        self.client.login(username='test@test.ru', password='2304test')
        url = reverse('order:history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

