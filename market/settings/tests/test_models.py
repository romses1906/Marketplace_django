from django.test import TestCase

from products.models import Product, Property, Category
from settings.models import Discount, DiscountOnCart


class DiscountModelTest(TestCase):
    """ Класс тестов модели Скидка """

    @classmethod
    def setUpTestData(cls):
        cls.property = Property.objects.create(name='тестовая характеристика')
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.product = Product.objects.create(
            name='Тестовый продукт',
            category=cls.category
        )
        cls.product.property.set([cls.property])
        cls.discount = Discount.objects.create(name='тестовая скидка на товар', description='тестовая скидка на товар',
                                               end_date='2023-06-28T17:11:37Z', value=10, value_type='percentage',
                                               active=True)
        cls.discount.products.set([cls.product])

    def test_verbose_name(self):
        """ Тестирование verbose_name полей модели Скидка """

        discount = self.discount
        field_verboses = {
            'name': 'наименование',
            'description': 'описание',
            'start_date': 'дата начала действия скидки',
            'end_date': 'дата окончания действия скидки',
            'created': 'создана',
            'value': 'значение скидки',
            'value_type': 'тип скидки',
            'active': 'активность',
            'products': 'продукты'

        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(discount._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        """ Тестирование максимально возможной длины для ввода поля name модели Скидка """

        discount = self.discount
        max_length = discount._meta.get_field('name').max_length
        self.assertEqual(max_length, 512)

    def test_description_max_length(self):
        """ Тестирование максимально возможной длины для ввода поля description модели Скидка """

        discount = self.discount
        max_length = discount._meta.get_field('description').max_length
        self.assertEqual(max_length, 2048)

    def test_blank_fields(self):
        """ Тестирование свойства blank полей модели Скидка """

        discount = self.discount
        blank_fields = [
            'description',
            'start_date',
        ]
        for field in blank_fields:
            with self.subTest(field=field):
                self.assertTrue(discount._meta.get_field(field_name=field).blank)

    def test_null_fields(self):
        """ Тестирование свойства null полей модели Скидка """

        discount = self.discount
        null_fields = [
            'start_date',
        ]
        for field in null_fields:
            with self.subTest(field=field):
                self.assertTrue(discount._meta.get_field(field_name=field).null)


class DiscountOnCartModelTest(TestCase):
    """ Класс тестов модели Скидка на корзину """

    @classmethod
    def setUpTestData(cls):
        cls.discount_on_cart = DiscountOnCart.objects.create(name='тестовая скидка на корзину',
                                                             description='тестовая скидка на корзину',
                                                             end_date='2023-06-28T17:11:37Z', value=10,
                                                             value_type='percentage',
                                                             active=True, quantity_at=1, quantity_to=3,
                                                             cart_total_price_at=500)

    def test_verbose_name(self):
        """ Тестирование verbose_name полей модели Скидка на корзину """

        discount_on_cart = self.discount_on_cart
        field_verboses = {
            'name': 'наименование',
            'description': 'описание',
            'start_date': 'дата начала действия скидки',
            'end_date': 'дата окончания действия скидки',
            'created': 'создана',
            'value': 'значение скидки',
            'value_type': 'тип скидки',
            'active': 'активность',
            'quantity_at': 'количество товаров в корзине от',
            'quantity_to': 'количество товаров в корзине до',
            'cart_total_price_at': 'общая стоимость товаров в корзине от'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(discount_on_cart._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        """ Тестирование максимально возможной длины для ввода поля name модели Скидка на корзину """

        discount_on_cart = self.discount_on_cart
        max_length = discount_on_cart._meta.get_field('name').max_length
        self.assertEqual(max_length, 512)

    def test_description_max_length(self):
        """ Тестирование максимально возможной длины для ввода поля description модели Скидка на корзину """

        discount_on_cart = self.discount_on_cart
        max_length = discount_on_cart._meta.get_field('description').max_length
        self.assertEqual(max_length, 2048)

    def test_blank_fields(self):
        """ Тестирование свойства blank полей модели Скидка на корзину """

        discount_on_cart = self.discount_on_cart
        blank_fields = [
            'description',
            'start_date',
        ]
        for field in blank_fields:
            with self.subTest(field=field):
                self.assertTrue(discount_on_cart._meta.get_field(field_name=field).blank)

    def test_null_fields(self):
        """ Тестирование свойства null полей модели Скидка на корзину """

        discount_on_cart = self.discount_on_cart
        null_fields = [
            'start_date',
        ]
        for field in null_fields:
            with self.subTest(field=field):
                self.assertTrue(discount_on_cart._meta.get_field(field_name=field).null)
