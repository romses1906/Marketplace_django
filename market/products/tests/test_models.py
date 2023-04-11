from django.test import TestCase
from products.models import Product, Property, ProductProperty, Category


class ProductModelTest(TestCase):
    """Класс тестов модели Продукт"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.property = Property.objects.create(name='тестовая характеристика')
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.product = Product.objects.create(
            name='Тестовый продукт',
            category=cls.category
        )
        cls.product.property.set([cls.property])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        ProductModelTest.property.delete()
        ProductModelTest.product.delete()

    def test_verbose_name(self):
        product = ProductModelTest.product
        field_verboses = {
            'name': 'наименование',
            'property': 'характеристики',
            'category': 'категория'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(product._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        product = ProductModelTest.product
        max_length = product._meta.get_field('name').max_length
        self.assertEqual(max_length, 512)


class PropertyModelTest(TestCase):
    """Класс тестов модели Свойство продукта"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.property = Property.objects.create(name='тестовая характеристика')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        PropertyModelTest.property.delete()

    def test_verbose_name(self):
        property = ProductModelTest.property
        field_verboses = {
            'name': 'наименование',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(property._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        property = ProductModelTest.property
        max_length = property._meta.get_field('name').max_length
        self.assertEqual(max_length, 512)


class ProductPropertyModelTest(TestCase):
    """Класс тестов модели Значение свойства продукта"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.property = Property.objects.create(name='тестовая характеристика')
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.product = Product.objects.create(
            name='Тестовый продукт',
            category=cls.category
        )
        cls.product_property = ProductProperty.objects.create(product=cls.product, property=cls.property,
                                                              value='тестовое значение характеристики')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        ProductPropertyModelTest.product.delete()
        ProductPropertyModelTest.property.delete()
        ProductPropertyModelTest.product_property.delete()

    def test_verbose_name(self):
        product_property = ProductPropertyModelTest.product_property
        field_verboses = {
            'value': 'значение',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(product_property._meta.get_field(field).verbose_name, expected_value)

    def test_value_max_length(self):
        product_property = ProductPropertyModelTest.product_property
        max_length = product_property._meta.get_field('value').max_length
        self.assertEqual(max_length, 128)
