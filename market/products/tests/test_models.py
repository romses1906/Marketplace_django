from django.test import TestCase

from products.models import Product, Property, ProductProperty, Category, ProductTag


class ProductModelTest(TestCase):
    """Класс тестов модели Продукт"""

    @classmethod
    def setUpTestData(cls):
        cls.property = Property.objects.create(name='тестовая характеристика')
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.product = Product.objects.create(
            name='Тестовый продукт',
            category=cls.category
        )
        cls.product.property.set([cls.property])

    def test_verbose_name(self):
        product = self.product
        field_verboses = {
            'name': 'наименование',
            'property': 'характеристики',
            'category': 'категория'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(product._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        product = self.product
        max_length = product._meta.get_field('name').max_length
        self.assertEqual(max_length, 512)


class PropertyModelTest(TestCase):
    """Класс тестов модели Свойство продукта"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.property = Property.objects.create(name='тестовая характеристика')

    def test_verbose_name(self):
        property = self.property
        field_verboses = {
            'name': 'наименование',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(property._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        property = self.property
        max_length = property._meta.get_field('name').max_length
        self.assertEqual(max_length, 512)


class ProductPropertyModelTest(TestCase):
    """Класс тестов модели Значение свойства продукта"""

    @classmethod
    def setUpTestData(cls):
        cls.property = Property.objects.create(name='тестовая характеристика')
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.product = Product.objects.create(
            name='Тестовый продукт',
            category=cls.category
        )
        cls.product_property = ProductProperty.objects.create(product=cls.product, property=cls.property,
                                                              value='тестовое значение характеристики')

    def test_verbose_name(self):
        product_property = self.product_property
        field_verboses = {
            'value': 'значение',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(product_property._meta.get_field(field).verbose_name, expected_value)

    def test_value_max_length(self):
        product_property = self.product_property
        max_length = product_property._meta.get_field('value').max_length
        self.assertEqual(max_length, 128)


class CategoryModelTest(TestCase):
    """Класс тестов модели Категория"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.category_child = Category.objects.create(name='вложенная категория',
                                                     description='тестовое описание вложенной категории',
                                                     parent=cls.category)

    def test_verbose_name(self):
        category = self.category
        field_verboses = {
            'name': 'наименование',
            'description': 'описание',
            'parent': 'родительская категория'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(category._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self):
        category = self.category
        max_length = category._meta.get_field('name').max_length
        self.assertEqual(max_length, 512)

    def test_description_max_length(self):
        category = self.category
        max_length = category._meta.get_field('description').max_length
        self.assertEqual(max_length, 512)

    def test_blank_fields(self):
        category = self.category
        blank_fields = [
            'image',
            'parent',
        ]
        for field in blank_fields:
            with self.subTest(field=field):
                self.assertTrue(category._meta.get_field(field_name=field).blank)

    def test_null_fields(self):
        category = self.category
        null_fields = [
            'image',
            'parent',
        ]
        for field in null_fields:
            with self.subTest(field=field):
                self.assertTrue(category._meta.get_field(field_name=field).blank)

    def test_parent_field(self):
        category = self.category
        category_child = self.category_child
        name_category_parent = category_child.parent.name
        self.assertEqual(name_category_parent, category.name)


class ProductTagModelTest(TestCase):
    """Класс тестов модели ProductTag"""

    @classmethod
    def setUpTestData(cls):
        cls.test_tags = 'test_tag_1', 'test_tag_2', 'test_tag_3'
        cls.tags = ProductTag.objects.create()
        cls.tags.tags.add(*cls.test_tags)

    def test_tags_names(self):
        self.assertEqual(tuple(self.tags.tags.names()), self.test_tags)
