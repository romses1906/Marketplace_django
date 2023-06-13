import json
from datetime import datetime

import stripe
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from order.models import Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateSessionView(LoginRequiredMixin, SuccessMessageMixin, View):
    """Представление для создания сессии на оплату."""

    def get(self, request, *args, **kwargs):
        """Метод для составления запроса на получение сессии."""
        # достаём данные о заказе и продуктах
        num_order = self.kwargs["order_id"]
        order = Order.objects.get(pk=num_order)
        items = OrderItem.objects.prefetch_related('offer__product').filter(order_id=order.pk)
        name_items = list()
        for item in items:
            name_items.append(item.offer.product.name)

        # создаём сессию для оплаты и проводим её через js
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': round(order.final_price) * 100,
                        'product_data': {
                            'name': _(f'Заказ №{num_order}, от {self.request.user.first_name}'),
                            "description": ', '.join(name_items)
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f'http://127.0.0.1:8000/pay/success_pay/{num_order}/',
            cancel_url=f'http://127.0.0.1:8000/pay/cancel_pay/{num_order}/',
        )

        return JsonResponse({
            'id': checkout_session.id
        })


class PaymentView(LoginRequiredMixin, TemplateView):
    """Представление страницы оплаты."""
    template_name = 'payment/payment.j2'

    def get_context_data(self, **kwargs):
        """Формирование данных для stripe.js"""
        context = super().get_context_data(**kwargs)
        context['data'] = json.dumps(
            {
                'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
                'order_id': self.kwargs['order_id']
            }
        )
        return context


class SuccessView(LoginRequiredMixin, TemplateView):
    """Представление подтверждения пройденной оплаты."""
    template_name = 'payment/progressPayment.j2'

    def get(self, request, *args, **kwargs):
        """Смена статуса заказа на оплаченный."""
        order_id = self.kwargs['order_id']
        Order.objects.filter(pk=order_id).update(status='pain', payment_date=datetime.now())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Добавление в контекст сообщения об успешной оплате."""
        order_id = self.kwargs['order_id']
        context = super().get_context_data()
        context['status'] = _(f'Заказ №{order_id} успешно оплачен!')
        return context


class CancelView(LoginRequiredMixin, TemplateView):
    """Представление по отмене оплаты."""
    template_name = 'payment/progressPayment.j2'

    def get_context_data(self, **kwargs):
        """Добавление в контекст сообщения об успешной оплате."""
        order_id = self.kwargs['order_id']
        context = super().get_context_data()
        context['status'] = _(f'Заказ №{order_id} не оплачен!')
        return context
