from cart.cart import CartServices
from django.test import TestCase, Client
from django.urls import reverse
from order.models import Order
from users.models import User


class UpdateSessionMixin:  # позволяет избежать повтора кода в test_view_creates_order_object_when_form_is_valid
    """ Класс-миксин для обновления информации в сессии """  # и test_order_price_is_correct

    @staticmethod
    def update_session(session):
        session['user_data'] = {
            'full_name': "Ivanov Ivan Ivanovich",
            'email': "ivan@mail.ru",
            'phone_number': "+79223891654"
        }
        session.save()
        session['shipping_data'] = {
            'delivery_option': "Delivery",
            'delivery_address': "Mira, 2",
            'delivery_city': "Minsk"
        }
        session.save()
        session['payment_data'] = {'payment_option': "Online Card"}
        session.save()


class TestOrderViews(TestCase):
    """
    Тест представлений оформления заказа
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test@test.ru', email='test@test.ru', password='2304test')
        cls.session = {}
        cls.client = Client()
        cls.request = cls.client.request().wsgi_request
        cls.request.session.update(cls.session)
        cls.cart = CartServices(cls.request)

        cls.client.login(username='test@test.ru', password='2304test')

        cls.user_data = {'full_name': 'Ivan Ivanovich Ivanov',
                         'email': 'ivan@mail.ru',
                         'phone_number': '+79072223340'}
        cls.shipping_data = {'delivery_option': 'Delivery',
                             'delivery_address': '123 Main St',
                             'delivery_city': 'New York'}
        cls.payment_data = {'payment_option': 'Online Card'}

        cls.order = Order.objects.create(user=cls.user, status='created', delivery_option='Delivery',
                                         delivery_address='Novgorodskay, 1', delivery_city='Moscow',
                                         payment_option='Online Card',
                                         comment='Comment 1')

    def test_step1_view(self):
        self.client.login(username='test@test.ru', password='2304test')
        response = self.client.get(reverse('order:step1'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('order:step1'), data=self.user_data)
        self.assertRedirects(response, reverse('order:step2'))

    def test_checkout_step1_by_an_unauthorized_user(self):
        response = self.client.get(reverse('order:step1'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('order:step1'), data=self.user_data)

        # Проверяем, что был создан новый пользователь
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())
        new_user = User.objects.filter(email=self.user_data['email']).first()
        self.assertEqual(new_user.first_name, 'Ivanovich')
        self.assertEqual(new_user.last_name, 'Ivan')
        self.assertEqual(new_user.surname, 'Ivanov')
        self.assertEqual(new_user.phone_number, '+79072223340')

    def test_step2_view(self):
        self.client.login(username='test@test.ru', password='2304test')
        response = self.client.get(reverse('order:step2'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('order:step2'), data=self.shipping_data)
        self.assertRedirects(response, reverse('order:step3'))

    def test_step3_view(self):
        self.client.login(username='test@test.ru', password='2304test')
        self.client.get(reverse('order:step2'))
        response = self.client.get(reverse('order:step3'))
        self.assertEqual(response.status_code, 200)
        self.client.post(reverse('order:step2'), data=self.shipping_data)
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


class Step4ViewTestCase(TestCase, UpdateSessionMixin):
    """
    Тест представления 4 шага оформления заказа
    """

    fixtures = [
        "004_groups.json",
        "005_users.json",
        "010_shops.json",
        "015_categories.json",
        "020_products.json",
        "030_offers.json",
        "050_cart.json",
        "055_productincart.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('order:step4')

    def test_view_redirects_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/users/login_user/?next={self.url}')

    def test_view_creates_order_object_when_form_is_valid(self):
        self.client.login(username='admin@admin.ru', password='admin')
        session = self.client.session
        self.update_session(session)
        response = self.client.post(self.url, {
            'comment': 'This is a test comment',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)

    def test_order_price_is_correct(self):
        """ Тестирование корректности цены заказа """

        self.client.login(username='admin@admin.ru', password='admin')
        session = self.client.session
        self.request = self.client.request().wsgi_request
        self.cart = CartServices(self.request)
        cart_price = self.cart.get_final_price_with_discount()
        self.update_session(session)
        response = self.client.post(self.url, {  # noqa F841
            'comment': 'This is a test comment',
        })
        total_order_price = Order.objects.first().final_price
        self.request = self.client.request().wsgi_request
        self.cart = CartServices(self.request)
        delivery_price = self.cart.get_delivery_cost()
        self.assertEqual(total_order_price, cart_price + delivery_price)
