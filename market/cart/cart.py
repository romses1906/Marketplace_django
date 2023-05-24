from decimal import Decimal
from typing import Dict

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Sum, F

from django.conf import settings
from shops.models import Offer
from cart.models import Cart, ProductInCart
from users.models import User


class CartServices:
    """
    Класс корзины пользователя
    """

    def __init__(self, request):
        self.use_db = False
        self.cart = None
        self.user = request.user
        self.session = request.session
        self.qs = None
        cart = self.session.get(settings.CART_SESSION_ID)
        if self.user.is_authenticated:
            self.use_db = True
            if cart:
                self.save_in_db(cart, request.user)
                self.clear(True)
            try:
                cart = Cart.objects.get(user=self.user, is_active=True)
            except ObjectDoesNotExist:
                cart = Cart.objects.create(user=self.user)
            self.qs = ProductInCart.objects.filter(cart=cart)
        else:
            # сохранить пустую корзину в сеансе
            if not cart:
                cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def save_in_db(self, cart: dict, user: User) -> None:
        """
        Перенос корзины из сессии в БД
        :param cart: корзина из сессии
        :param user: пользователь
        :return: None
        """
        try:
            cart_ = Cart.objects.get(user=user, is_active=True)
            cart_exists = True
        except ObjectDoesNotExist:
            cart_exists = False
        for key, value in cart.items():
            if cart_exists:
                try:
                    with transaction.atomic():  # FIXME убрать, применять при сохранении более чем в одну модель
                        product = ProductInCart.objects.filter(cart=cart_).select_for_update().get(offer=key)
                        product.quantity += cart[key]['quantity']
                        product.save()
                except ObjectDoesNotExist:
                    ProductInCart.objects.create(
                        offer=Offer.objects.get(pk=key),
                        cart=Cart.objects.filter(user=user, is_active=True).first(),
                        quantity=cart[key]['quantity']
                    )
            else:
                offer = Offer.objects.get(id=key)
                # TODO здесь можно применить transaction.atomic()
                cart_ = Cart.objects.create(user=user)
                ProductInCart.objects.create(
                    offer=offer,
                    cart=cart_,
                    quantity=value['quantity'],
                )

        self.session.pop(settings.CART_SESSION_ID, None)

    def add_user_data(self, form) -> None:
        """
        Добавить данные пользователя в корзину.
        :param form: Данные формы пользователя.
        :return: None
        """
        self.session['user_data'] = form.cleaned_data
        self.save()

    def add_shipping_data(self, form):
        """
        Добавить данные о доставке в корзину.
        :param form: Данные формы пользователя.
        :return: None
        """
        self.session['shipping_data'] = form.cleaned_data
        self.save()

    def add_payment_data(self, form):
        """
        Добавить данные об оплате в корзину.
        :param form: Данные формы пользователя.
        :return: None
        """
        self.session['payment_data'] = form.cleaned_data
        self.save()

    def get_user_data(self) -> Dict:
        """
        Получить данные пользователя из корзины.
        :return: Dict.
        """
        return self.session.get('user_data')

    def get_shipping_data(self) -> Dict:
        """
        Получить данные о доставке из корзины.
        """
        return self.session.get('shipping_data')

    def get_payment_data(self) -> Dict:
        """
        Получить данные об оплате из корзины.
        """
        return self.session.get('payment_data')

    def get_product_data(self, product_id) -> Dict:
        """
        Получение количества и стоимости товара в корзине по идентификатору.
        :param product_id: id продукта
        :return: Dict
        """
        if self.use_db:
            product = ProductInCart.objects.filter(cart=self.cart, offer=product_id).first()
            if product:
                quantity = product.quantity
                price = product.offer.price
                total_price = quantity * price
            else:
                quantity = 0
                price = 0
                total_price = 0
        else:
            if product_id in self.cart:
                quantity = self.cart[product_id]['quantity']
                price = Decimal(self.cart[product_id]['price'])
                total_price = quantity * price
            else:
                quantity = 0
                price = 0
                total_price = 0

        return {
            'quantity': quantity,
            'price': price,
            'total_price': total_price
        }

    def update(self, offer: Offer, quantity: int = 1, update_quantity: bool = False) -> None:
        """
        Добавляет товар в корзину и обновляет его количество
        :param offer: товар
        :param quantity: количество
        :param update_quantity: флаг, указывающий, нужно ли обновить товар (False) либо добавить его (True)
        :return: None
        """
        if self.use_db:
            if self.qs.filter(offer=offer).exists():
                with transaction.atomic():
                    product_in_cart = self.qs.select_for_update().get(offer=offer)
                product_in_cart.refresh_from_db()
            else:
                product_in_cart = ProductInCart(
                    offer=offer,
                    cart=self.cart,
                    quantity=0
                )
            if update_quantity:
                product_in_cart.quantity = quantity
            else:
                product_in_cart.quantity += quantity
            product_in_cart.save()
        else:
            product_id = str(offer.pk)
            if product_id not in self.cart:
                self.cart[product_id] = {'quantity': quantity,
                                         'price': str(offer.price)}
            elif update_quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id]['quantity'] += quantity
            self.save()

    def save(self) -> None:
        """
        Сохранение корзины в сессии
        :return: None
        """
        if not self.use_db:
            # обновить корзину сеансов
            self.session[settings.CART_SESSION_ID] = self.cart
            # пометить сеанс как «измененный», чтобы убедиться, что он сохранен
            self.session.modified = True

    def remove(self, offer: Offer) -> None:
        """
        Удаление товара из корзины
        :param offer: товар
        :return: None
        """
        if self.use_db:
            product_ = self.qs.filter(offer=offer)
            if product_.exists():
                product_.delete()
        else:
            product_id = str(offer.id)
            if product_id in self.cart:
                del self.cart[product_id]
                self.save()

    def __iter__(self):
        """
        Перебор товаров из корзины
        :return:
        """
        offer_ids = self.cart.keys()
        # получить объекты продукта и добавить их в корзину
        offers = Offer.objects.filter(id__in=offer_ids)
        for offer in offers:
            self.cart[str(offer.id)]['offer'] = offer

        for item in self.cart.values():
            item['quantity'] = int(item['quantity'])
            item['price'] = Decimal(item['offer'].price)
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self) -> int:
        """
        Считает количество товаров в корзине
        :return: количество товаров в корзине
        """
        if self.use_db:
            result = ProductInCart.objects.filter(cart=self.cart).aggregate(Sum('quantity'))['quantity__sum']
            return result if result else 0
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        """
        Считает итоговую цену товаров корзины
        :return: цена товаров в корзине
        """
        if self.use_db:
            total = self.qs.only('quantity', 'offer__price').aggregate(total=Sum(F('quantity') * F('offer__price')))[
                'total']
            if not total:
                total = Decimal('0')
            return total.quantize(Decimal('1.00'))
        else:
            return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self, only_session: bool = False) -> None:
        """
        Удалить корзину из сеанса или из базы данных, если пользователь авторизован
        :return:
        """
        if only_session:
            if settings.CART_SESSION_ID in self.session:
                del self.session[settings.CART_SESSION_ID]
                self.session.modified = True
        else:
            if self.qs:
                self.qs.delete()
            if settings.CART_SESSION_ID in self.session:
                del self.session[settings.CART_SESSION_ID]
                self.session.modified = True
