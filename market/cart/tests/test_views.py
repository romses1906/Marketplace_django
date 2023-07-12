import os

from django.test import signals
from django.urls import reverse
from jinja2 import Template as Jinja2Template
from django.test import TestCase, Client

from cart.models import Cart
from config.settings import FIXTURE_DIRS

ORIGINAL_JINJA2_RENDERER = Jinja2Template.render


def instrumented_render(template_object, *args, **kwargs):
    """ Переопределение метода рендеринга шаблонов Jinja2 """

    context = dict(*args, **kwargs)
    signals.template_rendered.send(
        sender=template_object,
        template=template_object,
        context=context
    )
    return ORIGINAL_JINJA2_RENDERER(template_object, *args, **kwargs)


Jinja2Template.render = instrumented_render


class CartViewTest(TestCase):
    """Тестирование представлений корзины пользователя."""

    fixtures = os.listdir(*FIXTURE_DIRS)

    def setUp(self):
        self.client = Client()
        self.url = reverse('cart:cart')

    def test_cart_view_context(self):
        self.client.login(username='admin@admin.ru', password='admin')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "cart/cart.j2")
        self.assertEqual(response.status_code, 200)
        cart_items = response.context_data['cart_items']
        cart_total_price = response.context_data['cart_total_price']
        cart_final_price_with_discount = response.context_data['cart_final_price_with_discount']
        self.assertEqual(len(cart_items), 2)
        self.assertEqual(cart_total_price, 1400.00)
        self.assertEqual(cart_final_price_with_discount, 1100.00)
        name = cart_items[1].offer.product.name
        self.assertIn('Евгений Онегин', name)

    def test_update_cart_view(self):
        url = reverse('cart:update_to_cart')
        response = self.client.post(url, {
            'product_id': 6,
            'quantity': 1
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'product_id': '6',
            'product_quantity': '1',
            'product_total_price': '300.00',
            'cart_total_price': '300.00',
            'cart_final_price_with_discount': '200.00',
            'disc_price': '200.00',
            'cart_len': '1'
        })

    def test_remove_from_cart_view(self):
        url = reverse('cart:remove_from_cart', kwargs={'product_id': 6})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('cart:cart'))
        self.assertEqual(Cart.objects.filter(user_id=1, is_active=True).count(), 1)
