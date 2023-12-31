from datetime import datetime
from decimal import Decimal

from cart.cart import CartServices
from django.db.models import QuerySet, Sum
from django.test import TestCase, Client
from django.utils import timezone

from settings.models import Discount, DiscountOnCart, DiscountOnSet, SiteSettings
from shops.models import Offer, Shop
from users.models import User


class CartTestCase(TestCase):
    """Класс теста корзины пользователя"""
    fixtures = [
        "004_groups.json",
        "005_users.json",
        "010_shops.json",
        "015_categories.json",
        "020_products.json",
        "030_offers.json",
        "050_cart.json",
        "055_productincart.json",
        "075_discounts.json",
        "080_discounts_on_cart.json",
        "085_discounts_on_set",
        "090_products_in_set",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='ivan', email='ivan@mail.ru', password='Password123')
        cls.offer = Offer.objects.first()
        cls.session = {}
        cls.client = Client()
        cls.request = cls.client.request().wsgi_request
        cls.request.session.update(cls.session)
        cls.cart = CartServices(cls.request)
        cls.date_now = datetime.now(tz=timezone.utc)
        cls.discounts = Discount.objects.filter(end_date__gte=cls.date_now)
        cls.discounts_on_cart = DiscountOnCart.objects.filter(end_date__gte=cls.date_now)
        cls.discounts_on_set = DiscountOnSet.objects.filter(end_date__gte=cls.date_now)
        cls.offer_with_discounts = Offer.objects.get(id=6)  # онегин
        cls.offer_in_discount_on_set = Offer.objects.get(id=17)  # яблоко
        cls.offer1 = Offer.objects.get(id=1)  # магазин 1
        cls.offer2 = Offer.objects.get(id=4)  # магазин 3
        cls.min_order_price_for_free_shipping = SiteSettings.load().min_order_price_for_free_shipping
        cls.min_deliv_cost = SiteSettings.load().standard_order_price
        cls.express = SiteSettings.load().express_order_price
        cls.standard = SiteSettings.load().standard_order_price
        cls.deliv_cost_express = cls.express + cls.standard

    def test_add_to_cart(self):
        """Тестирование функции add класса Cart"""
        self.cart.update(self.offer)
        self.assertEqual(len(self.cart), 1)
        self.assertEqual(self.cart.get_total_price(), self.offer.price)

    def test_update_cart(self):
        """Тестирование функции update класса Cart"""
        self.cart.update(self.offer)
        self.cart.update(self.offer, quantity=2, update_quantity=True)

        self.assertEqual(len(self.cart), 2)
        self.assertEqual(self.cart.get_total_price(), self.offer.price * 2)

    def test_remove_from_cart(self):
        """Тестирование функции remove класса Cart"""
        self.cart.update(self.offer)
        self.cart.remove(self.offer)

        self.assertEqual(len(self.cart), 0)
        self.assertEqual(self.cart.get_total_price(), Decimal('0'))

    def test_clear_cart(self):
        """Тестирование функции clear класса Cart"""
        self.cart.update(self.offer)
        self.cart.remove(self.offer)
        self.cart.clear()

        self.assertEqual(len(self.cart), 0)
        self.assertEqual(self.cart.get_total_price(), Decimal('0'))

    def test_get_shops_with_products_not_empty_dict(self):
        """Тестирование метода получения списка магазинов предлогающих товар."""
        self.cart.update(self.offer, 2)
        shops_by_product = self.cart.get_shops_with_products()
        self.assertGreater(len(shops_by_product), 0)

    def test_get_shops_with_products_all_shops_offer_goods(self):
        """Тестирование метода получения списка магазинов предлогающих товар."""
        shops_by_product = self.cart.get_shops_with_products()
        product_ids = self.cart.get_products_id()

        for product_id in product_ids:
            for shop in shops_by_product[product_id]:
                offers = shop.offer_set.filter(product_id=product_id, in_stock__gte=1)
                self.assertGreaterEqual(offers.count(), 1)

    def test_update_shops_with_products(self):
        """Тестирование метода обновления предложения при изменении магазина."""
        old_offer = Offer.objects.filter(pk=17).first()
        new_shop = Shop.objects.filter(pk=5).first()
        new_offer = Offer.objects.filter(pk=18).first()
        self.cart.update(old_offer, 2)
        old_offer_in_cart = self.cart.cart[str(old_offer.id)]
        self.assertEqual(Decimal(old_offer_in_cart["price"]), Decimal(100))
        self.assertEqual(old_offer_in_cart["quantity"], 2)
        with self.assertRaises(KeyError):
            self.cart.cart[str(new_offer.id)]

        self.cart.update_shops_with_products(offer_id=old_offer.id, shop_id=new_shop.id)

        with self.assertRaises(KeyError):
            self.cart.cart[str(old_offer.id)]
        new_offer_in_cart = self.cart.cart[str(new_offer.id)]
        self.assertEqual(Decimal(new_offer_in_cart["price"]), Decimal(102))
        self.assertEqual(new_offer_in_cart["quantity"], 2)

    def test_get_products_id(self):
        """Тестирование метода получения id товаров в корзине."""
        self.cart.update(self.offer, 2)
        product_ids = self.cart.get_products_id()
        self.assertTrue(isinstance(product_ids, QuerySet))

    def test_get_min_price_on_product_with_discount(self):
        """ Тестирование метода получения минимальной цены на товар с учетом действующих на этот товар скидок """

        discounts_on_product = self.discounts.filter(products__id=self.offer_with_discounts.product.id)
        min_price_on_product = self.cart.get_min_price_on_product_with_discount(price=self.offer_with_discounts.price,
                                                                                discounts=discounts_on_product)
        disc_prices_lst = []
        for discount in discounts_on_product:
            disc_price = 0
            if discount.value_type == 'percentage':
                disc_price = self.offer_with_discounts.price * Decimal((1 - discount.value / 100))
            elif discount.value_type == 'fixed_amount':
                disc_price = self.offer_with_discounts.price - discount.value
            elif discount.value_type == 'fixed_price':
                disc_price = discount.value
            if disc_price > 0:
                disc_prices_lst.append(disc_price)
            else:
                disc_prices_lst.append(1)
        self.assertEqual(min_price_on_product, min(disc_prices_lst))

    def test_get_total_price_with_discount_on_cart(self):
        """ Тестирование метода получения общей стоимости товаров в корзине с учетом действующей скидки на корзину """

        added_offer = Offer.objects.get(id=10)
        self.cart.update(added_offer, 3)
        for discount in self.discounts_on_cart:
            disc_total_price = 0
            if discount.value_type == 'percentage':
                disc_total_price = self.cart.get_total_price() * Decimal((1 - discount.value / 100))
            elif discount.value_type == 'fixed_amount':
                disc_total_price = self.cart.get_total_price() - discount.value
            elif discount.value_type == 'fixed_price':
                disc_total_price = discount.value
            self.assertEqual(self.cart.get_total_price_with_discount_on_cart(discount, self.cart.get_total_price()),
                             disc_total_price)

    def test_get_min_total_price_with_discount_on_cart(self):
        """ Тестирование метода получения общей минимальной стоимости товаров в
        корзине с учетом действующих скидок на корзину
        """
        added_offer = Offer.objects.get(id=10)
        self.cart.update(added_offer, 3)
        disc_total_prices_on_cart_lst = []
        for discount in self.discounts_on_cart:
            if discount.quantity_at <= self.cart.__len__() <= discount.quantity_to \
                    and self.cart.get_total_price() >= discount.cart_total_price_at:
                disc_total_price = self.cart.get_total_price_with_discount_on_cart(
                    discount=discount,
                    total_price=self.cart.get_total_price())
                disc_total_prices_on_cart_lst.append(disc_total_price)
            else:
                disc_total_prices_on_cart_lst.append(self.cart.get_total_price())
        disc_total_price_on_cart = self.cart.get_min_total_price_with_discount_on_cart()
        self.assertEqual(disc_total_price_on_cart, min(disc_total_prices_on_cart_lst))

    def test_get_total_price_with_discounts_on_products(self):
        """ Тестирование метода получения итоговой стоимости корзины с учетом скидок на товары """

        self.cart.update(self.offer)
        self.cart.update(self.offer_with_discounts, 2)
        total_price_with_discounts_on_products = self.cart.get_total_price_with_discounts_on_products()
        total = 0
        for item in self.cart.__iter__():
            discounts = Discount.objects.filter(end_date__gte=self.date_now, products__id=item['offer'].product.id)
            if discounts:
                disc_price = self.cart.get_min_price_on_product_with_discount(price=item['price'],
                                                                              discounts=discounts)
                total += disc_price * item['quantity']
            else:
                total += item['price'] * item['quantity']
        self.assertEqual(total_price_with_discounts_on_products, total)

    def test_get_total_price_with_discount_on_set(self):
        """ Тестирование метода получения общей стоимости товаров в корзине с учетом действующей скидки на набор """

        self.cart.update(self.offer_with_discounts, 1)
        self.cart.update(self.offer_in_discount_on_set, 1)
        total_price_on_set = self.offer_with_discounts.price + self.offer_in_discount_on_set.price
        for discount in self.discounts_on_set:
            disc = 0
            if discount.value_type == 'percentage':
                disc = total_price_on_set * Decimal(discount.value / 100)
            elif discount.value_type == 'fixed_amount':
                disc = discount.value
            elif discount.value_type == 'fixed_price':
                disc = total_price_on_set - discount.value
            disc_total_price = Decimal(self.cart.get_total_price() - disc).quantize(Decimal('1.00'))
            self.assertEqual(self.cart.get_total_price_with_discount_on_set(discount, self.cart.get_total_price(),
                                                                            total_price_on_set), disc_total_price)

    def test_get_min_total_price_with_discount_on_set(self):
        """ Тестирование метода получения общей минимальной стоимости товаров в
        корзине с учетом действующих скидок на наборы товаров
        """
        # получаем еще один продукт из имеющегося скидочного набора
        offer_in_discount_on_set_2 = Offer.objects.get(id=7)
        # добавляем товары в корзину
        self.cart.update(self.offer_with_discounts, 1)
        self.cart.update(self.offer_in_discount_on_set, 1)
        self.cart.update(offer_in_discount_on_set_2, 2)
        total_price = self.cart.get_total_price()
        disc_total_prices_on_cart_lst = [total_price]
        product_in_cart_ids = list(self.cart.get_products_id())
        offer_ids = []
        # получаем id предложений в корзине
        for item in self.cart.__iter__():
            offer_ids.append(item['offer'].id)
        for discount in self.discounts_on_set:
            # получаем id товаров в скидочном наборе
            products_in_set_ids = [item[0] for item in
                                   discount.products_in_set.all().values_list('product__id')]
            # проверяем, что все товары из данного скидочного набора есть в корзине
            if set(products_in_set_ids).issubset(product_in_cart_ids):
                # получаем суммарную стоимость товаров в скидочном наборе
                total_price_on_set = Offer.objects.filter(id__in=offer_ids,
                                                          product__id__in=products_in_set_ids).aggregate(
                    Sum('price'))['price__sum']
                disc_total_price = self.cart.get_total_price_with_discount_on_set(discount=discount,
                                                                                  total_price=total_price,
                                                                                  total_price_on_set=total_price_on_set
                                                                                  )
                disc_total_prices_on_cart_lst.append(disc_total_price)
        disc_total_price_on_cart = self.cart.get_min_total_price_with_discount_on_set()
        # проверяем, что стоимость корзины, посчитанная "вручную", равна стоимости, посчитанной в методе
        self.assertEqual(disc_total_price_on_cart, min(disc_total_prices_on_cart_lst))

    def test_get_final_price_with_discount(self):
        """ Тестирование метода получения финальной стоимости корзины товаров после применения приоритетной скидки """

        # воспроизводим сценарий, чтобы сработала скидка на корзину или на набор
        # (какая "тяжелее", та сработает, данные виды скидок приоритетнее скидок на товары)
        added_offer = Offer.objects.get(id=10)
        self.cart.update(added_offer, 3)
        self.cart.update(self.offer_with_discounts, 1)
        # получаем еще один продукт из имеющегося скидочного набора
        offer_in_discount_on_set_2 = Offer.objects.get(id=7)
        # добавляем товар в корзину
        self.cart.update(offer_in_discount_on_set_2, 1)
        total_price_with_discount_on_cart_or_set = min(total_price() for total_price in (
            self.cart.get_min_total_price_with_discount_on_cart, self.cart.get_min_total_price_with_discount_on_set))
        cart_final_price_with_discount = self.cart.get_final_price_with_discount()
        self.assertEqual(cart_final_price_with_discount, total_price_with_discount_on_cart_or_set)

        # воспроизводим сценарий, при котором скидка на корзину или набор не срабатывает (не выполнены условия),
        # а срабатывает скидка на отдельный товар (на этот товар есть скидка в БД изначально)
        self.cart.remove(added_offer)
        self.cart.remove(offer_in_discount_on_set_2)
        self.cart.update(self.offer_with_discounts, quantity=1, update_quantity=True)
        cart_final_price_with_discount_after_removing_added_offer = self.cart.get_final_price_with_discount()
        total_price_with_discounts_on_products = self.cart.get_total_price_with_discounts_on_products()
        self.assertEqual(cart_final_price_with_discount_after_removing_added_offer,
                         total_price_with_discounts_on_products)

    def test_has_single_seller(self):
        """ Положительный тест метода, который проверяет все ли товары в корзине из одного магазина"""

        self.cart.update(self.offer1)
        self.cart.update(self.offer1)
        self.assertTrue(self.cart.has_single_seller())

    def test_does_not_have_single_seller(self):
        """ Негативный тест метода, который проверяет все ли товары в корзине из одного магазина"""
        self.cart.update(self.offer1)
        self.cart.update(self.offer2)
        self.assertFalse(self.cart.has_single_seller())

    def test_get_delivery_cost_with_standard_delivery(self):
        """ Тестирование метода получения стоимости стандартной доставки"""

        self.cart.session['shipping_data'] = {
            'delivery_option': "Delivery",
            'delivery_address': "Mira, 2",
            'delivery_city': "Minsk"
        }

        self.cart.update(self.offer1)
        if self.min_order_price_for_free_shipping > self.cart.get_total_price():
            # не выполнены условия для бесплатной доставки
            self.assertEqual(self.cart.get_delivery_cost(), self.min_deliv_cost)
        else:
            # Видимо изменили min_order_price_for_free_shipping в SiteSettings и условия выполнились
            self.assertEqual(self.cart.get_delivery_cost(), Decimal("0"))

        self.cart.update(offer=self.offer1, quantity=40)
        if self.min_order_price_for_free_shipping <= self.cart.get_total_price():
            # Выполнены все условия
            self.assertEqual(self.cart.get_delivery_cost(), Decimal("0"))
            # Не выполнено условия, что все товары из одного магазина
            self.cart.update(offer=self.offer2)
            self.assertEqual(self.cart.get_delivery_cost(), self.min_deliv_cost)
        else:
            # Видимо изменили min_order_price_for_free_shipping в SiteSettings, и условие не выполнилось
            self.assertEqual(self.cart.get_delivery_cost(), self.min_deliv_cost)
            # Не выполнены все условия
            self.cart.update(offer=self.offer2)
            self.assertEqual(self.cart.get_delivery_cost(), self.min_deliv_cost)

    def test_get_delivery_cost_with_express_delivery(self):
        """ Тестирование метода получения стоимости экспресс доставки"""

        self.cart.session['shipping_data'] = {
            'delivery_option': "Express Delivery",
            'delivery_address': "Mira, 2",
            'delivery_city': "Minsk"
        }

        self.cart.update(self.offer1)
        if self.min_order_price_for_free_shipping > self.cart.get_total_price():
            # не выполнены условия для бесплатной доставки
            self.assertEqual(self.cart.get_delivery_cost(), self.deliv_cost_express)
        else:
            # Видимо изменили min_order_price_for_free_shipping в SiteSettings и условия выполнились
            self.assertEqual(self.cart.get_delivery_cost(), self.express)

        self.cart.update(offer=self.offer1, quantity=40)
        if self.min_order_price_for_free_shipping <= self.cart.get_total_price():
            # Выполнены все условия
            self.assertEqual(self.cart.get_delivery_cost(), self.express)
            # Не выполнено условия, что все товары из одного магазина
            self.cart.update(offer=self.offer2)
            self.assertEqual(self.cart.get_delivery_cost(), self.deliv_cost_express)
        else:
            # Видимо изменили min_order_price_for_free_shipping в SiteSettings, и условие не выполнилось
            self.assertEqual(self.cart.get_delivery_cost(), self.deliv_cost_express)
            # Не выполнены все условия
            self.cart.update(offer=self.offer2)
            self.assertEqual(self.cart.get_delivery_cost(), self.deliv_cost_express)

    def test_get_product_data(self):
        """ Тестирование метода получения данных предложения добавленного в корзину по его id"""

        self.cart.update(self.offer1, 2)

        product_data = self.cart.get_product_data(product_id="1")

        self.assertEqual(product_data['quantity'], 2)
        self.assertEqual(product_data['price'], 350)
        self.assertEqual(product_data['disc_price'], 350)
        self.assertEqual(product_data['total_price'], 700)
