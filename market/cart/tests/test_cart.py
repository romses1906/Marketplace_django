from decimal import Decimal

from django.db.models import QuerySet
from django.test import TestCase, Client

from shops.models import Offer, Shop
from cart.cart import CartServices
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

    def test_has_single_seller(self):
        """Тестирование метода проверки корзины на наличие товаров только от одного продавца."""
        self.cart.update(self.offer, 2)
        self.assertTrue(self.cart.has_single_seller())
