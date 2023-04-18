from decimal import Decimal
from django.conf import settings
from shops.models import Offer


class Cart:
    def __init__(self, request):
        """
        Инициализируем корзину
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.delivery = None
        self.delivery_fee = Decimal('0')

    def add_delivery(self, delivery):
        """
        Добавить информацию о доставке в корзину.
        """
        self.delivery = delivery
        self.save()

    def calculate_shipping(self):
        """
        Подсчет стоимости доставки и общей стоимости корзины.
        """
        if not self.delivery:
            return Decimal('0')
        if self.get_total_price() >= self.delivery.order_total_for_free_delivery:
            self.delivery_fee = Decimal('0')
        elif self.delivery.delivery_option == 'Express Delivery':
            self.delivery_fee = Decimal(self.delivery.express_delivery_fee)
        else:
            self.delivery_fee = Decimal(self.delivery.delivery_fee)
        return self.delivery_fee

    def add(self, offer, quantity=1, update_quantity=False):
        """
        Добавить продукт в корзину или обновить его количество.
        """
        if not offer:
            return
        product_id = str(offer.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(offer.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        """
        Сохранение изменений корзины.
        """
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session[settings.DELIVERY_SESSION_ID] = self.delivery.id if self.delivery else None
        if 'modified' not in self.session:
            self.session['modified'] = True
        else:
            self.session.modified = True

    def remove(self, offer):
        """
        Удаление товара из корзины.
        """
        if not offer:
            return
        product_id = str(offer.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        offer_ids = self.cart.keys()
        offers = Offer.objects.filter(id__in=offer_ids)
        for offer in offers:
            self.cart[str(offer.id)]['offer'] = offer

        for item in self.cart.values():
            if 'offer' not in item:
                continue
            item['price'] = Decimal(item['offer'].price)
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.cart.values())

    def clear(self):
        """
        Удаление корзины из сессии.
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
