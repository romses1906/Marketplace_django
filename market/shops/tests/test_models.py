import os

from django.contrib.auth import get_user_model
from django.test import TestCase

from products.models import Product, Property, Category
from shops.models import Shop, Offer, Banner, phone_validate
from users.models import User


class ShopModelTest(TestCase):
    """ Класс тестов модели Магазин """

    @classmethod
    def setUpTestData(cls):
        cls.property = Property.objects.create(name='тестовая характеристика')
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.product = Product.objects.create(
            name='тестовый продукт',
            category=cls.category
        )
        cls.product.property.set([cls.property])
        cls.user = User.objects.create_user(email="test@test.com", password="testpassword")
        cls.shop = Shop.objects.create(name='тестовый магазин', user=cls.user)
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=25)

    def test_verbose_name(self):
        """ Тестирование verbose_name модели Магазин """

        shop = self.shop
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
        """ Тестирование максимальной длины для поля name модели Магазин """

        shop = self.shop
        max_length = shop._meta.get_field('name').max_length
        self.assertEqual(max_length, 512)

    def test_phone_number_max_length(self):
        """ Тестирование максимальной длины для поля phone_number модели Магазин """

        shop = self.shop
        max_length = shop._meta.get_field('phone_number').max_length
        self.assertEqual(max_length, 18)

    def test_address_max_length(self):
        """ Тестирование максимальной длины для поля address модели Магазин """

        shop = self.shop
        max_length = shop._meta.get_field('address').max_length
        self.assertEqual(max_length, 255)

    def test_email_max_length(self):
        """ Тестирование максимальной длины для поля email модели Магазин """

        shop = self.shop
        max_length = shop._meta.get_field('email').max_length
        self.assertEqual(max_length, 255)

    def test_blank(self):
        """ Тестирование свойства blank для набора полей модели Магазин """

        shop = self.shop
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
        """ Тестирование свойства null для набора полей модели Магазин """

        shop = self.shop
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
        """ Тестирование корректности валидации данных в поле phone_number модели Магазин """

        shop = self.shop
        field = shop._meta.get_field(field_name='phone_number')
        self.assertIn(phone_validate, field.validators)
        self.assertEqual(phone_validate.regex.pattern, r'^\+\d{1,3}\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$')


class OfferModelTest(TestCase):
    """ Класс тестов модели Предложение магазина """

    @classmethod
    def setUpClass(cls):
        cls.user = get_user_model().objects.create_user(email='admin@megano.ru', password='secret')
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.product = Product.objects.create(
            name='тестовый продукт',
            category=cls.category
        )
        cls.shop = Shop.objects.create(name='тестовый магазин', user=cls.user)
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=35)

    @classmethod
    def tearDownClass(cls):
        cls.offer.delete()
        cls.product.delete()
        cls.shop.delete()
        cls.user.delete()

    def test_verbose_name(self):
        """ Тестирование verbose_name модели Предложение магазина """

        offer = self.offer
        field_verboses = {
            'price': 'цена',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(offer._meta.get_field(field).verbose_name, expected_value)

    def test_price_max_digits(self):
        """ Тестирование свойства max_digits поля price модели Предложение магазина """

        offer = self.offer
        max_digits = offer._meta.get_field('price').max_digits
        self.assertEqual(max_digits, 10)

    def test_price_decimal_places(self):
        """ Тестирование свойства decimal_places поля price модели Предложение магазина """

        offer = self.offer
        decimal_places = offer._meta.get_field('price').decimal_places
        self.assertEqual(decimal_places, 2)


class BannerManagerTestCase(TestCase):
    """Класс тестов менеджера баннеров"""

    def setUp(self):
        Banner.objects.create(
            title='Banner 1',
            description='Banner 1 description',
            is_active=True,
            link='https://example.com'
        )
        Banner.objects.create(
            title='Banner 2',
            description='Banner 2 description',
            is_active=True,
            link='https://example.com'
        )
        Banner.objects.create(
            title='Banner 3',
            description='Banner 3 description',
            is_active=False,
            link='https://example.com'
        )
        Banner.objects.create(
            title='Banner 4',
            description='Banner 4 description',
            is_active=True,
            link='https://example.com'
        )

    def test_get_active_banners(self):
        """ Тестирование корректности получения действующих баннеров """

        active_banners = Banner.objects.get_active_banners()
        self.assertEqual(len(active_banners), 3)
        for banner in active_banners:
            self.assertTrue(banner.is_active)

    def test_active_banners_random_order(self):
        active_banners_1 = Banner.objects.get_active_banners()
        active_banners_2 = Banner.objects.get_active_banners()
        self.assertNotEqual(active_banners_1, active_banners_2)


class BannerTestCase(TestCase):
    """Класс тестов модели Баннер"""

    def test_create_banner(self):
        """ Тестирование корректности создания баннера """
        banner = Banner.objects.create(
            image='banners/banner.jpg',
            title='MAVIC PRO 5 MINI DRONE',
            description='Get the best phone you ever seen with modern Windows OS plus 70% Off this summer',
            is_active=True,
            link='https://example.com'
        )

        self.assertEqual(os.path.basename(banner.image.path), 'banner.jpg')
        self.assertEqual(banner.title, 'MAVIC PRO 5 MINI DRONE')
        self.assertEqual(banner.description, 'Get the best phone you ever seen with modern Windows OS plus 70% Off '
                                             'this summer')
        self.assertTrue(banner.is_active)
        self.assertEqual(banner.link, 'https://example.com')
        self.assertEqual(str(banner), 'MAVIC PRO 5 MINI DRONE')


class UsersShopsTests(TestCase):
    fixtures = [
        '004_groups.json',
        '005_users.json',
        '010_shops.json'
    ]

    def test_create_user(self):
        self.assertEqual(Shop.objects.count(), 5)
