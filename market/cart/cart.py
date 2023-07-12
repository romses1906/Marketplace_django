from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Dict

from cart.models import Cart, ProductInCart
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Sum, F, QuerySet
from django.utils import timezone
from products.models import Product
from settings.models import Discount, DiscountOnCart, DiscountOnSet
from settings.models import SiteSettings
from shops.models import Offer, Shop
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
        self.date_now = datetime.now(tz=timezone.utc)
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
                    product = ProductInCart.objects.filter(cart=cart_).get(offer=key)
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
                with transaction.atomic():
                    cart_ = Cart.objects.create(user=user)
                    ProductInCart.objects.create(
                        offer=offer,
                        cart=cart_,
                        quantity=value['quantity'],
                    )

        self.session.pop(settings.CART_SESSION_ID, None)

    def get_shops_with_products(self) -> Dict:
        """
        Получения словаря магазинов, которые предлагают необходимый товар.
        :return: Dict
        """
        product_ids = self.get_products_id()
        if self.use_db:
            shops_by_product = defaultdict(set)
            qs = Offer.objects.filter(product_id__in=product_ids, in_stock__gte=1).select_related('shop')
            for product_id in product_ids:
                for offer in qs.filter(product_id=product_id):
                    shops_by_product[product_id].add(offer.shop)
        else:
            qs = Offer.objects.filter(product_id__in=product_ids, in_stock__gte=1).select_related('shop')
            shops_by_product = defaultdict(set)
            for product_id in product_ids:
                for offer in qs.filter(product_id=product_id):
                    if str(offer.id) in self.cart:
                        shops_by_product[product_id].add(offer.shop)

                for shop in Shop.objects.filter(offers__product_id=product_id):
                    if shop not in shops_by_product[product_id]:
                        shops_by_product[product_id].add(shop)
        return shops_by_product

    def update_shops_with_products(self, offer_id, shop_id) -> None:
        """
        Обновление предложения товара, в соответствии с выбранным продуктом.
        :param offer_id: id предложеия
        :param shop_id: id магазина
        :return: None
        """
        offer = Offer.objects.select_related('product').get(id=offer_id)
        product_id = offer.product.id
        new_offer = Offer.objects.filter(shop_id=shop_id, product_id=product_id).select_related('product').first()

        if self.use_db:
            item_cart = ProductInCart.objects.filter(cart=self.cart, offer_id=offer_id).select_related('offer').first()
            quantity = item_cart.quantity
        else:
            item_cart = self.cart[str(offer_id)]
            quantity = item_cart["quantity"]
        if quantity > 0:
            with transaction.atomic():
                self.update(offer=new_offer, quantity=quantity)
                self.remove(offer)

    def add_user_data(self, form) -> None:
        """
        Добавить данные пользователя в корзину.
        :param form: Данные формы пользователя.
        :return: None
        """
        self.session['user_data'] = form.cleaned_data
        self.save()

    def add_shipping_data(self, form) -> None:
        """
        Добавить данные о доставке в корзину.
        :param form: Данные формы пользователя.
        :return: None
        """
        self.session['shipping_data'] = form.cleaned_data
        self.save()

    def add_payment_data(self, form) -> None:
        """
        Добавить данные об оплате в корзину.
        :param form: Данные формы пользователя.
        :return: None
        """
        self.session['payment_data'] = form.cleaned_data
        self.save()

    def get_products_id(self) -> QuerySet:
        """
        Получает id всех продуктов в корзине
        :return: QuerySet
        """
        if self.use_db:
            product_ids = ProductInCart.objects.filter(cart=self.cart, cart__is_active=True) \
                .values_list('offer__product_id', flat=True).distinct()
        else:
            offer_ids = self.cart.keys()
            product_ids = Offer.objects.filter(id__in=offer_ids).values_list('product_id', flat=True)
        return product_ids

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
                discounts = Discount.objects.filter(end_date__gte=self.date_now, products__id=product.offer.product.id)
                if discounts:
                    disc_price = self.get_min_price_on_product_with_discount(price=product.offer.price,
                                                                             discounts=discounts)
                else:
                    disc_price = price
            else:
                quantity = 0
                price = 0
                disc_price = 0
                total_price = 0
        else:
            if product_id in self.cart:
                quantity = self.cart[product_id]['quantity']
                price = Decimal(self.cart[product_id]['price'])
                disc_price = Decimal(self.cart[str(product_id)]['disc_price'])
                total_price = quantity * price
            else:
                quantity = 0
                price = 0
                disc_price = 0
                total_price = 0

        return {
            'quantity': quantity,
            'price': price,
            'disc_price': disc_price.quantize(Decimal('1.00')) if disc_price > 0 else 1,
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
        if offer.in_stock >= quantity:
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
                discounts = Discount.objects.filter(end_date__gte=self.date_now, products__id=offer.product.id)
                if discounts:
                    disc_price = self.get_min_price_on_product_with_discount(price=offer.price, discounts=discounts)
                else:
                    disc_price = offer.price
                if product_id not in self.cart:
                    self.cart[product_id] = {'quantity': quantity,
                                             'price': str(offer.price)}
                elif update_quantity:
                    self.cart[product_id]['quantity'] = quantity
                else:
                    self.cart[product_id]['quantity'] += quantity
                self.cart[product_id]['disc_price'] = str(Decimal(disc_price).quantize(Decimal('1.00')))
                self.save()
        else:
            raise ValueError("Товар закончился на складе. Вы можете поискать его в другом магазине.")

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
        offers = Offer.objects.filter(id__in=offer_ids, in_stock__gte=1)
        for offer in offers:
            self.cart[str(offer.id)]['offer'] = offer

        for item in self.cart.values():
            if 'offer' in item:
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
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_total_price_with_discounts_on_products(self) -> Decimal:
        """
        Считает итоговую стоимость корзины с учетом скидок на товары

        :return: общая цена товаров в корзине с учетом скидок на эти товары
        """
        ids = [item[0] for item in
               Product.objects.select_related('category').prefetch_related('property', 'tags', 'discounts').
               filter(discounts__end_date__gte=self.date_now).values_list('id')]

        total = 0
        if self.use_db:
            for item in self.qs.all():
                if item.offer.product.id in ids:
                    discounts = Discount.objects.filter(end_date__gte=self.date_now,
                                                        products__id=item.offer.product.id)
                    disc_price = self.get_min_price_on_product_with_discount(price=item.offer.price,
                                                                             discounts=discounts)
                    total += item.quantity * disc_price
                else:
                    total += item.quantity * item.offer.price
            return Decimal(total).quantize(Decimal('1.00'))
        return sum(Decimal(item['disc_price']) * item['quantity'] for item in self.cart.values())

    def get_min_price_on_product_with_discount(self, price: Decimal, discounts: QuerySet) -> Decimal:
        """
        Считает минимальную цену товара в корзине с учетом действующих на этот товар скидок

        :return: минимальная цена товара в корзине с учетом действующих на этот товар скидок
        """

        disc_prices_lst = []
        for discount in discounts:
            disc_price = 0
            if discount.value_type == 'percentage':
                disc_price = price * Decimal((1 - discount.value / 100))
            elif discount.value_type == 'fixed_amount':
                disc_price = price - discount.value
            elif discount.value_type == 'fixed_price':
                disc_price = discount.value
            if disc_price > 0:
                disc_prices_lst.append(disc_price)
            else:
                disc_prices_lst.append(1)
        disc_price = min(disc_prices_lst)
        return disc_price

    def get_min_total_price_with_discount_on_cart(self) -> Decimal:
        """
        Считает общую минимальную стоимость товаров в корзине с учетом действующих скидок на корзину

        :return: общая минимальная стоимость товаров в корзине с учетом действующих скидок на корзину
        """
        discounts = DiscountOnCart.objects.filter(end_date__gte=self.date_now)
        total_price = self.get_total_price()
        total_quantity = self.__len__()
        disc_total_prices_on_cart_lst = []
        if discounts:
            for discount in discounts:
                if discount.quantity_at <= total_quantity <= discount.quantity_to \
                        and total_price >= discount.cart_total_price_at:
                    disc_total_price = self.get_total_price_with_discount_on_cart(discount=discount,
                                                                                  total_price=total_price)
                    disc_total_prices_on_cart_lst.append(disc_total_price)
                else:
                    disc_total_prices_on_cart_lst.append(total_price)
        else:
            disc_total_prices_on_cart_lst.append(total_price)
        disc_total_price_on_cart = min(disc_total_prices_on_cart_lst)
        return Decimal(disc_total_price_on_cart).quantize(Decimal('1.00'))

    def get_total_price_with_discount_on_cart(self, discount: Discount, total_price: Decimal) -> Decimal:
        """
        Считает общую стоимость товаров в корзине с учетом действующей скидки на корзину

        :return: общая стоимость товаров в корзине с учетом действующей скидки на корзину
        """

        disc_total_price = 0
        if discount.value_type == 'percentage':
            disc_total_price = total_price * Decimal((1 - discount.value / 100))
        elif discount.value_type == 'fixed_amount':
            disc_total_price = total_price - discount.value
        elif discount.value_type == 'fixed_price':
            disc_total_price = discount.value
        return disc_total_price

    def get_min_total_price_with_discount_on_set(self):
        """
        Считает общую минимальную стоимость товаров в корзине с учетом действующих скидок на наборы товаров

        :return: общая минимальная стоимость товаров в корзине с учетом действующих скидок на наборы товаров
        """
        discounts = DiscountOnSet.objects.filter(end_date__gte=self.date_now)
        total_price = self.get_total_price()
        disc_total_prices_on_cart_lst = [total_price]
        if self.use_db:
            for discount in discounts:
                # получаем id товаров из скидочного набора
                products_in_set_ids = [item[0] for item in
                                       discount.products_in_set.all().values_list('product__id')]
                # получаем товары из корзины, которые есть в скидочном наборе
                find_products_in_cart = self.qs.filter(offer__product__id__in=products_in_set_ids)
                # проверяем, есть ли среди товаров корзины товары из скидочного набора, а также проверяем количество
                # таких товаров (в случае, если товар участвует в нескольких скидочных наборах, может быть применена
                # не та скидка, т.к. найдется например один товар из двух и скидка сработает все равно)
                if find_products_in_cart.exists() and len(products_in_set_ids) == find_products_in_cart.count():
                    total_price_on_set = 0
                    for item in self.qs.filter(offer__product__id__in=products_in_set_ids):
                        total_price_on_set += item.offer.price
                    disc_total_price = self.get_total_price_with_discount_on_set(discount=discount,
                                                                                 total_price=total_price,
                                                                                 total_price_on_set=total_price_on_set)
                    disc_total_prices_on_cart_lst.append(disc_total_price)
            # обработать случай, когда после скидки получим отрицательное
        else:
            # получаем id товаров в корзине
            product_in_cart_ids = list(self.get_products_id())
            for discount in discounts:
                # получаем id товаров в скидочном наборе
                products_in_set_ids = [item[0] for item in
                                       discount.products_in_set.all().values_list('product__id')]
                # проверяем, что все товары из данного скидочного набора есть в корзине
                if set(products_in_set_ids).issubset(product_in_cart_ids):
                    # получаем суммарную стоимость товаров в скидочном наборе
                    total_price_on_set = Offer.objects.filter(id__in=self.cart.keys(),
                                                              product__id__in=products_in_set_ids).aggregate(
                        Sum('price'))['price__sum']
                    disc_total_price = self.get_total_price_with_discount_on_set(discount=discount,
                                                                                 total_price=total_price,
                                                                                 total_price_on_set=total_price_on_set)
                    disc_total_prices_on_cart_lst.append(disc_total_price)
        return min(disc_total_prices_on_cart_lst)

    def get_total_price_with_discount_on_set(self, discount: DiscountOnSet, total_price: Decimal,
                                             total_price_on_set) -> Decimal:
        """
        Считает общую стоимость товаров в корзине с учетом действующей скидки на набор товаров

        :return: общая стоимость товаров в корзине с учетом действующей скидки на набор товаров
        """
        disc = 0
        if discount.value_type == 'percentage':
            disc = total_price_on_set * Decimal(discount.value / 100)
        elif discount.value_type == 'fixed_amount':
            disc = discount.value
        elif discount.value_type == 'fixed_price':
            disc = total_price_on_set - discount.value
        disc_total_price = Decimal(total_price - disc).quantize(Decimal('1.00'))
        return disc_total_price

    def get_final_price_with_discount(self) -> Decimal:
        """
        Метод определения финальной стоимости корзины товаров после применения приоритетной скидки

        :return: финальная стоимость корзины товаров после применения приоритетной скидки
        """

        total_price = self.get_total_price()
        total_price_with_discount_on_cart_or_set = min(total_price() for total_price in (
            self.get_min_total_price_with_discount_on_cart, self.get_min_total_price_with_discount_on_set))

        if total_price_with_discount_on_cart_or_set < total_price:
            return total_price_with_discount_on_cart_or_set
        return self.get_total_price_with_discounts_on_products()

    def get_delivery_cost(self) -> Decimal:
        """
        Получает стоимость доставки
        :return: Decimal
        """
        try:
            delivery_option = self.get_shipping_data()["delivery_option"]
            delivery_cost = Decimal(0)
            total_cost = self.get_total_price()
            min_order_price_for_free_shipping = SiteSettings.load().min_order_price_for_free_shipping

            if delivery_option == 'Delivery':
                min_deliv_cost = SiteSettings.load().standard_order_price
                if total_cost < min_order_price_for_free_shipping or not self.has_single_seller():
                    delivery_cost = Decimal(min_deliv_cost).quantize(Decimal('1.00'))

            elif delivery_option == 'Express Delivery':
                express = SiteSettings.load().express_order_price
                standard = SiteSettings.load().standard_order_price
                min_deliv_cost = express + standard
                if total_cost < min_order_price_for_free_shipping or not self.has_single_seller():
                    delivery_cost = Decimal(min_deliv_cost).quantize(Decimal('1.00'))
                else:
                    delivery_cost = Decimal(express).quantize(Decimal('1.00'))
            return delivery_cost
        except TypeError:
            return 'Не был выбран способ доставки!'

    def has_single_seller(self) -> bool:
        """
        В корзине все товары от одного продавца
        :return: bool
        """
        product_ids = self.get_products_id()
        offers = Offer.objects.filter(id__in=product_ids)
        sellers = set(offers.values_list('shop_id', flat=True))
        return len(sellers) == 1

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

    def check_cart_products_availability(self, request) -> None:
        """
        Проверяет наличие товаров в корзине на складе и удаляет товары, которых нет на складе
        """
        product_ids = self.get_products_id()
        qs = Offer.objects.filter(product_id__in=product_ids, in_stock=0)
        if qs:
            for item in qs:
                messages.warning(request, f'{item.product.name} закончился на складе магазина {item.shop.name}')
                self.remove(item)
                self.save()
