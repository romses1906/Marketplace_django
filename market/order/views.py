from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, CreateView, DetailView, ListView

from cart.cart import CartServices
from cart.models import ProductInCart
from order.models import Order
from order.forms import UserForm, DeliveryForm, PaymentForm, CommentForm
from order.services import add_items_from_cart
from users.models import User
from users.services import create_user


class Step1View(View):
    """
    Отображает страницу первого шага заказа
    """
    template_name = 'order/step1.j2'
    form_class = UserForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(email=request.user.email)
            full_name = f"{user.last_name} {user.first_name} {user.surname}"
            form = self.form_class(initial={
                'full_name': full_name,
                'email': user.email,
                'phone_number': user.phone_number
            })
        else:
            form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user_data = {
                'full_name': form.cleaned_data['full_name'],
                'email': form.cleaned_data['email'],
                'phone_number': form.cleaned_data['phone_number']
            }
            if not request.user.is_authenticated:
                create_user(request, user_data)
            cart = CartServices(request)
            cart.add_user_data(form)
            return redirect('order:step2')
        return render(request, self.template_name, {'form': form})


class Step2View(LoginRequiredMixin, FormView):
    """
    Отображает страницу второго шага заказа
    """
    template_name = 'order/step2.j2'
    form_class = DeliveryForm
    success_url = reverse_lazy('order:step3')
    login_url = reverse_lazy('users:login_user')

    def form_valid(self, form):
        shipping_data = {  # noqa F841
            'delivery_option': form.cleaned_data['delivery_option'],
            'delivery_address': form.cleaned_data['delivery_address'],
            'delivery_city': form.cleaned_data['delivery_city']
        }
        cart = CartServices(self.request)
        cart.add_shipping_data(form)

        return super().form_valid(form)


class Step3View(LoginRequiredMixin, FormView):
    """
    Отображает страницу третьего шага заказа
    """
    template_name = 'order/step3.j2'
    form_class = PaymentForm
    success_url = reverse_lazy('order:step4')
    login_url = reverse_lazy('users:login_user')

    def form_valid(self, form):
        payment_data = {  # noqa F841
            'payment_option': form.cleaned_data['payment_option'],
        }
        cart = CartServices(self.request)
        cart.add_payment_data(form)
        return super().form_valid(form)


class Step4View(LoginRequiredMixin, CreateView):
    """
    Отображает страницу четвертого шага заказа
    """
    model = Order
    form_class = CommentForm
    template_name = 'order/step4.j2'
    success_url = reverse_lazy('order:history')
    login_url = reverse_lazy('users:login_user')

    def get_queryset(self):
        cart = CartServices(self.request)
        return ProductInCart.objects.filter(cart=cart).select_related('offer')

    def form_valid(self, form):
        cart = CartServices(self.request)

        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.full_name = cart.get_user_data()['full_name']
            self.object.delivery_option = cart.get_shipping_data()['delivery_option']
            self.object.delivery_address = cart.get_shipping_data()['delivery_address']
            self.object.delivery_city = cart.get_shipping_data()['delivery_city']
            self.object.payment_option = cart.get_payment_data()['payment_option']
            self.object.comment = form.cleaned_data['comment']
            self.object.save()
            add_items_from_cart(self.object, cart)
            cart.clear()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartServices(self.request)
        context['order_items'] = cart.qs
        context['get_total_price'] = cart.get_total_price()
        context['user_data'] = cart.get_user_data()
        context['shipping_data'] = cart.get_shipping_data()
        context['payment_data'] = cart.get_payment_data()
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Отображает детальную страницу заказа
    """
    model = Order
    template_name = 'order/detail_order.j2'
    context_object_name = 'order'
    login_url = reverse_lazy('users:login_user')

    def get_queryset(self):
        return Order.objects.select_related('user').prefetch_related('offer__product', 'items__offer__product')


class OrderListView(LoginRequiredMixin, ListView):
    """
    Отображает страницу истории заказов пользователя
    """
    model = Order
    template_name = 'order/history.j2'
    context_object_name = 'orders'
    login_url = reverse_lazy('users:login_user')

    def get_queryset(self):
        return Order.objects.select_related('user').filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
