from django.test import TestCase
from order.forms import UserForm, DeliveryForm, PaymentForm, CommentForm


class UserFormTest(TestCase):
    """Класс теста формы внесения данных пользователя в заказ"""

    def test_user_form_valid(self):
        form_data = {'full_name': 'John Doe', 'email': 'john@example.com', 'phone_number': '1234567890'}
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_form_invalid(self):
        form_data = {'full_name': '', 'email': '', 'phone_number': ''}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())


class DeliveryFormTest(TestCase):
    """Класс теста формы внесения информации о доставке в заказ"""

    def test_delivery_form_valid(self):
        form_data = {'delivery_option': 'Delivery', 'delivery_address': '123 Main St', 'delivery_city': 'New York'}
        form = DeliveryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_delivery_form_invalid(self):
        form_data = {'delivery_option': '', 'delivery_address': '', 'delivery_city': ''}
        form = DeliveryForm(data=form_data)
        self.assertFalse(form.is_valid())


class PaymentFormTest(TestCase):
    """Класс теста формы внесения информации об оплате в заказ"""

    def test_payment_form_valid(self):
        form_data = {'payment_option': 'Online Card'}
        form = PaymentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_payment_form_invalid(self):
        form_data = {'payment_option': ''}
        form = PaymentForm(data=form_data)
        self.assertFalse(form.is_valid())


class CommentFormTest(TestCase):
    """Класс теста формы внесения комментария к оформлению заказа"""

    def test_comment_form_valid(self):
        form_data = {'comment': 'This is a test comment'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_invalid(self):
        form_data = {'comment': 'a' * 201}
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
