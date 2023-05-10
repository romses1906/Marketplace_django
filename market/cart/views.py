from django.http import JsonResponse
from django.views.generic.base import RedirectView, TemplateView, View
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.detail import SingleObjectMixin

from cart.cart import CartServices
from shops.models import Offer


class CartView(TemplateView):
    """
    Отображает корзину пользователя сайта
    """
    template_name = 'cart/cart.j2'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_services = CartServices(self.request)
        if cart_services.use_db:
            cart = cart_services.qs
        else:
            cart = cart_services
        context['cart_items'] = cart
        context['cart_total_price'] = cart_services.get_total_price()
        return context


class UpdateCartView(View):
    """
    Обнавляет количество товара в корзине
    """

    def post(self, request):
        cart = CartServices(request)
        product_id = request.POST.get('product_id', None)
        user_quantity = request.POST.get('quantity', None)
        offer = get_object_or_404(Offer, id=product_id)
        if product_id and user_quantity:
            cart.update(offer=offer, quantity=int(user_quantity), update_quantity=True)

        else:
            return JsonResponse({}, status=400)

        product_data = cart.get_product_data(product_id)
        if product_data:
            quantity = product_data['quantity']
            total_price = product_data['total_price']
            data = {
                'product_id': str(product_id),
                'product_quantity': str(quantity),
                'product_total_price': str(total_price),
                'cart_total_price': str(cart.get_total_price()),
                'cart_len': str(cart.__len__()),
            }
            return JsonResponse(data)


class RemoveFromCartView(RedirectView):
    """
    Полностью удаляет выбранный товар из корзины
    """
    url = reverse_lazy('cart:cart')

    def get_redirect_url(self, *args, **kwargs):
        product_id = self.kwargs['product_id']
        cart = CartServices(self.request)
        offer = Offer.objects.get(id=product_id)
        cart.remove(offer=offer)
        return super().get_redirect_url(*args, **kwargs)
