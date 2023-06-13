from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest
from django.test import TestCase

from comparison.comparison import Comparison
from products.models import Product, Category


class ComparisonTestCase(TestCase):
    """ Класс тестирования сервиса добавления товаров в сравнение. """

    @classmethod
    def setUpTestData(cls):
        cls.request = HttpRequest()
        cls.request.session = SessionBase()
        cls.compare = Comparison(cls.request)
        cls.category = Category.objects.create(
            name="test_category",
            description="test description"
        )
        cls.product_1 = Product.objects.create(
            name="test_1",
            category=cls.category
        )
        cls.product_2 = Product.objects.create(
            name="test_2",
            category=cls.category
        )

    def test_add_the_product_to_compare(self):
        self.compare.add(self.product_1)
        compare = self.compare.session.get(settings.COMPARE_SESSION_ID)
        category_id = str(self.category.id)
        category_name = self.category.name
        product_id = str(self.product_1.id)
        self.assertIsNotNone(compare)
        self.assertIn(category_id, compare)
        self.assertIn(category_name, compare[category_id][0])
        self.assertIn(product_id, compare[category_id][1])
        self.assertDictEqual({}, compare[category_id][1][product_id])

    def test_removing_not_the_last_product_in_the_category(self):
        self.compare.add(self.product_1)
        self.compare.add(self.product_2)
        category_id = str(self.category.id)
        product_id = str(self.product_1.id)
        self.compare.remove_product(category_id, product_id)
        compare = self.compare.session.get(settings.COMPARE_SESSION_ID)
        self.assertNotIn(product_id, compare[category_id][1])
        count = len(compare[category_id][1])
        self.assertTrue(count > 0)

    def test_removing_the_last_product_in_the_category(self):
        self.compare.add(self.product_1)
        category_id = str(self.category.id)
        product_id = str(self.product_1.id)
        self.compare.remove_product(category_id, product_id)
        compare = self.compare.session.get(settings.COMPARE_SESSION_ID)
        self.assertNotIn(category_id, compare)

    def test_removing_the_category(self):
        self.compare.add(self.product_1)
        category_id = str(self.category.id)
        self.compare.remove_category(category_id)
        compare = self.compare.session.get(settings.COMPARE_SESSION_ID)
        self.assertNotIn(category_id, compare)

    def test_clearing_the_comparison_session(self):
        self.compare.add(self.product_1)
        self.compare.clear()
        compare = self.compare.session.get(settings.COMPARE_SESSION_ID)
        self.assertIsNone(compare)
