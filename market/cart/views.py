from django.contrib import messages
from django.http import JsonResponse
from django.views.generic.base import RedirectView, TemplateView, View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse

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
        cart_services.check_cart_products_availability(self.request)
        if cart_services.use_db:
            cart = cart_services.qs
        else:
            cart = cart_services
        context['cart_items'] = cart
        context['cart_total_price'] = cart_services.get_total_price()
        context['shops_by_product'] = cart_services.get_shops_with_products()
        context['cart_final_price_with_discount'] = cart_services.get_final_price_with_discount()
        return context

    def post(self, request):
        cart_services = CartServices(request)
        shop_id = request.POST.get('shop_id')
        offer_id = request.POST.get('product_id')
        cart_services.update_shops_with_products(offer_id=offer_id, shop_id=shop_id)
        return redirect("cart:cart")


class UpdateCartView(View):
    """
    Обнавляет количество товара в корзине
    """

    def post(self, request):
        cart = CartServices(request)
        offer_id = request.POST.get('product_id')
        user_quantity = request.POST.get('quantity')
        offer = get_object_or_404(Offer, id=offer_id)

        if offer_id and user_quantity:
            try:
                cart.update(offer=offer, quantity=int(user_quantity), update_quantity=True)
            except ValueError:
                error_message = f'Извините, но на складе есть, только {offer.in_stock} шт.'
                return JsonResponse({'error': error_message}, status=400)
        else:
            error_message = 'Не удалось обновить корзину'
            return JsonResponse({'error': error_message}, status=400)

        product_data = cart.get_product_data(offer_id)
        if product_data:
            quantity = product_data['quantity']
            total_price = product_data['total_price']
            disc_price = product_data['disc_price']
            data = {
                'product_id': str(offer_id),
                'product_quantity': str(quantity),
                'disc_price': str(disc_price),
                'product_total_price': str(total_price),
                'cart_total_price': str(cart.get_total_price()),
                'cart_final_price_with_discount': str(cart.get_final_price_with_discount()),
                'cart_len': str(cart.__len__()),
            }
            return JsonResponse(data)


class RemoveFromCartView(RedirectView):
    """
    Полностью удаляет выбранный товар из корзины
    """
    url = reverse_lazy('cart:cart')

    def get_redirect_url(self, *args, **kwargs):
        offer_id = self.kwargs['product_id']
        cart = CartServices(self.request)
        offer = Offer.objects.get(id=offer_id)
        cart.remove(offer=offer)
        return super().get_redirect_url(*args, **kwargs)


class AddToCartView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        offer_id = self.kwargs['product_id']
        quantity = int(self.request.GET.get('quantity', 1))
        cart = CartServices(self.request)
        offer = Offer.objects.get(id=offer_id)
        try:
            cart.update(offer=offer, quantity=quantity, update_quantity=False)
            return_url = reverse('cart:cart')
        except ValueError as e:
            messages.error(self.request, str(e))
            return_url = self.request.META.get('HTTP_REFERER', '/')

        return return_url
