from django.test import TestCase, Client
from django.urls import reverse, resolve

from products.models import Product, Category
from reviews.views import CreateReviewsView


class ProductDetailPageTest(TestCase):
    """Тестирование URL добавления отзывов на продукт."""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.product = Product.objects.create(name='тестовый продукт', category=cls.category)
        cls.url = reverse('reviews:product_reviews', kwargs={'pk': cls.product.pk})
        cls.response = cls.client.get(cls.url)

    def test_page_uses_the_url_success(self):
        """Тестирование используемого URL."""

        self.assertURLEqual(self.url, f"/reviews/create/{self.product.pk}/")

    def test_url_uses_the_desired_view_success(self):
        """Тестирование используемого представлением URL."""

        view = resolve(self.url)
        self.assertEqual(view.func.__name__, CreateReviewsView.as_view().__name__)
