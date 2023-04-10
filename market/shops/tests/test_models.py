import re

from django.test import TestCase
from shops.models import Shop, Offer, phone_validate
from products.models import Product, Property


class ShopModelTest(TestCase):
    """Класс тестов модели Магазин"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.property = Property.objects.create(name='тестовая характеристика')
        cls.product = Product.objects.create(
            name='тестовый продукт',
        )
        cls.product.property.set([cls.property])
        cls.shop = Shop.objects.create(name='тестовый магазин')
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=25)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        ShopModelTest.property.delete()
        ShopModelTest.product.delete()
        ShopModelTest.shop.delete()
        ShopModelTest.offer.delete()

    def test_verbose_name(self):
        shop = ShopModelTest.shop
        field_verboses = {
            'name': 'название',
            'products': 'товары в магазине',
            'description': 'описание магазина',
            'phone_number': 'номер телефона',
            'address': 'адрес',
            'email': 'email',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(shop._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        shop = ShopModelTest.shop
        max_length = shop._meta.get_field('name').max_length
        self.assertEqual(max_length, 512)

    def test_phone_number_max_length(self):
        shop = ShopModelTest.shop
        max_length = shop._meta.get_field('phone_number').max_length
        self.assertEqual(max_length, 12)

    def test_address_max_length(self):
        shop = ShopModelTest.shop
        max_length = shop._meta.get_field('address').max_length
        self.assertEqual(max_length, 255)

    def test_email_max_length(self):
        shop = ShopModelTest.shop
        max_length = shop._meta.get_field('email').max_length
        self.assertEqual(max_length, 255)

    def test_blank(self):
        shop = ShopModelTest.shop
        blank_fields = [
            'description',
            'phone_number',
            'address',
            'email'
        ]
        for field in blank_fields:
            with self.subTest(field=field):
                self.assertTrue(shop._meta.get_field(field_name=field).blank)

    def test_null(self):
        shop = ShopModelTest.shop
        blank_fields = [
            'description',
            'phone_number',
            'address',
            'email'
        ]
        for field in blank_fields:
            with self.subTest(field=field):
                self.assertTrue(shop._meta.get_field(field_name=field).null)

    def test_phone_number_validation(self):
        shop = ShopModelTest.shop
        field = shop._meta.get_field(field_name='phone_number')
        self.assertIn(phone_validate, field.validators)
        self.assertEqual(phone_validate.regex.pattern, r'^\+?[78]\d{10}$')


class OfferModelTest(TestCase):
    """Класс тестов модели Предложение магазина"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = Product.objects.create(
            name='тестовый продукт',
        )
        cls.shop = Shop.objects.create(name='тестовый магазин')
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=35)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        OfferModelTest.product.delete()
        OfferModelTest.shop.delete()
        OfferModelTest.offer.delete()

    def test_verbose_name(self):
        offer = OfferModelTest.offer
        field_verboses = {
            'price': 'цена',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(offer._meta.get_field(field).verbose_name, expected_value)

    def test_price_max_digits(self):
        offer = OfferModelTest.offer
        max_digits = offer._meta.get_field('price').max_digits
        self.assertEqual(max_digits, 10)

    def test_price_decimal_places(self):
        offer = OfferModelTest.offer
        decimal_places = offer._meta.get_field('price').decimal_places
        self.assertEqual(decimal_places, 2)
