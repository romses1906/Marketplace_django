import os

from config.settings import FIXTURE_DIRS
from django.test import TestCase, Client
from django.urls import reverse, resolve
from settings.views import DiscountsListView


class DiscountsListPageTest(TestCase):
    """ Тестирование URL страницы для отображения скидок """

    fixtures = os.listdir(*FIXTURE_DIRS)

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse("settings:sales")

    def test_page_uses_the_correct_url(self):
        """ Тестирование используемого URL """

        self.assertURLEqual(self.url, "/settings/sales/")

    def test_url_uses_the_desired_view(self):
        """ Тестирование использования ожидаемого представления по данному URL """

        view = resolve(self.url)
        desired_view = DiscountsListView.as_view().__name__
        self.assertEqual(view.func.__name__, desired_view)
