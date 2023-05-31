from django.test import SimpleTestCase
from django.urls import reverse, resolve

from comparison.views import CompareDetail, add_compare_view


class TestUrls(SimpleTestCase):
    """ Класс тестирования urls сравнения товаров """

    def test_compare_detail_uses_correct_view(self):
        url = reverse("comparison:compare-detail")
        self.assertEqual(resolve(url).func.view_class, CompareDetail)

    def test_add_to_compare_uses_correct_view(self):
        url = reverse("comparison:add-to-compare", args=["1"])
        self.assertEqual(resolve(url).func, add_compare_view)
