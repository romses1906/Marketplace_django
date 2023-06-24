from django.db import IntegrityError
from django.test import TestCase
from products.models import Product, Property, Category
from settings.models import Discount, DiscountOnCart, DiscountOnSet, ProductInDiscountOnSet


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
                                               end_date='2023-07-28T17:11:37Z', value=10, value_type='percentage')
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

    def test_end_date_greater_start_date(self):
        """
        Тестирование ограничения для полей модели БД,
        содержащих даты начала и конца периода действия скидки на товар
        """

        constraint_name = "check_dates_in_discount"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Discount.objects.create(name='тестовая скидка на товар', description='тестовая скидка на товар',
                                    start_date='2023-07-28T17:11:37Z', end_date='2023-06-28T17:11:37Z',
                                    value=10, value_type='percentage')


class DiscountOnCartModelTest(TestCase):
    """ Класс тестов модели Скидка на корзину """

    @classmethod
    def setUpTestData(cls):
        cls.discount_on_cart = DiscountOnCart.objects.create(name='тестовая скидка на корзину',
                                                             description='тестовая скидка на корзину',
                                                             end_date='2023-07-28T17:11:37Z', value=10,
                                                             value_type='percentage',
                                                             quantity_at=1, quantity_to=3,
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

    def test_end_date_greater_start_date(self):
        """
        Тестирование ограничения для полей модели БД,
        содержащих даты начала и конца периода действия скидки на корзину
        """

        constraint_name = "check_dates_in_discount_on_cart"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            DiscountOnCart.objects.create(name='тестовая скидка на корзину',
                                          description='тестовая скидка на корзину',
                                          start_date='2023-07-28T17:11:37Z',
                                          end_date='2023-06-28T17:11:37Z', value=10,
                                          value_type='percentage',
                                          quantity_at=1, quantity_to=3,
                                          cart_total_price_at=500)


class DiscountOnSetModelTest(TestCase):
    """ Класс тестов модели Скидка на набор товаров """

    @classmethod
    def setUpTestData(cls):
        cls.discount_on_set = DiscountOnSet.objects.create(name='тестовая скидка на набо',
                                                           description='тестовая скидка на набор',
                                                           end_date='2023-07-28T17:11:37Z', value=50,
                                                           value_type='percentage')

    def test_verbose_name(self):
        """ Тестирование verbose_name полей модели Скидка на набор товаров """

        discount_on_set = self.discount_on_set
        field_verboses = {
            'name': 'наименование',
            'description': 'описание',
            'start_date': 'дата начала действия скидки',
            'end_date': 'дата окончания действия скидки',
            'created': 'создана',
            'value': 'значение скидки',
            'value_type': 'тип скидки',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(discount_on_set._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        """ Тестирование максимально возможной длины для ввода поля name модели Скидка на набор товаров """

        discount_on_set = self.discount_on_set
        max_length = discount_on_set._meta.get_field('name').max_length
        self.assertEqual(max_length, 512)

    def test_description_max_length(self):
        """ Тестирование максимально возможной длины для ввода поля description модели Скидка на набор товаров """

        discount_on_set = self.discount_on_set
        max_length = discount_on_set._meta.get_field('description').max_length
        self.assertEqual(max_length, 2048)

    def test_blank_fields(self):
        """ Тестирование свойства blank полей модели Скидка на набор товаров """

        discount_on_set = self.discount_on_set
        blank_fields = [
            'description',
            'start_date',
        ]
        for field in blank_fields:
            with self.subTest(field=field):
                self.assertTrue(discount_on_set._meta.get_field(field_name=field).blank)

    def test_null_fields(self):
        """ Тестирование свойства null полей модели Скидка на набор товаров """

        discount_on_set = self.discount_on_set
        null_fields = [
            'start_date',
        ]
        for field in null_fields:
            with self.subTest(field=field):
                self.assertTrue(discount_on_set._meta.get_field(field_name=field).null)

    def test_end_date_greater_start_date(self):
        """
        Тестирование ограничения для полей модели БД,
        содержащих даты начала и конца периода действия скидки на набор товаров
        """

        constraint_name = "check_dates_in_discount_on_set"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            DiscountOnSet.objects.create(name='тестовая скидка на набо',
                                         description='тестовая скидка на набор',
                                         start_date='2023-07-28T17:11:37Z',
                                         end_date='2023-6-28T17:11:37Z', value=50,
                                         value_type='percentage')


class ProductInDiscountOnSetModelTest(TestCase):
    """ Класс тестов модели Товары из наборов со скидкой """

    @classmethod
    def setUpTestData(cls):
        cls.discount_on_set = DiscountOnSet.objects.create(name='тестовая скидка на набо',
                                                           description='тестовая скидка на набор',
                                                           end_date='2023-07-28T17:11:37Z', value=50,
                                                           value_type='percentage')
        cls.property = Property.objects.create(name='тестовая характеристика')
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.product = Product.objects.create(
            name='Тестовый продукт',
            category=cls.category
        )
        cls.product.property.set([cls.property])
        cls.product_in_set = ProductInDiscountOnSet.objects.create(product=cls.product, discount=cls.discount_on_set)

    def test_verbose_name(self):
        """ Тестирование verbose_name полей модели Товары из наборов со скидкой """

        product_in_set = self.product_in_set
        field_verboses = {
            'product': 'продукт',
            'discount': 'скидка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(product_in_set._meta.get_field(field).verbose_name, expected_value)
