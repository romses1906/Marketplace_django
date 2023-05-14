from django.http import HttpRequest
from django.test import TestCase
from django.contrib.sessions.backends.base import SessionBase
from django.conf import settings


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
        cls.product = Product.objects.create(
            name="test",
            category=cls.category
        )

    def test_add_the_product_to_compare(self):
        self.compare.add(self.product)
        compare = self.request.session.get(settings.COMPARE_SESSION_ID)
        self.assertIsNotNone(compare)
