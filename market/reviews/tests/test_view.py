from django.test import TestCase, Client
from django.urls import reverse

from products.models import Category, Product
from users.models import User


class ReviewsCreateViewTests(TestCase):
    """Тестирование представления добавление отзыва на продукт."""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create(username='test', email='test@test.ru', password='test')
        cls.category = Category.objects.create(name='тестовая категория', description='тестовое описание категории')
        cls.product = Product.objects.create(name='тестовый продукт', category=cls.category)
        cls.url = reverse('reviews:product_reviews', kwargs={'pk': cls.product.pk})

    def test_post_review_success(self):
        """Проверка запроса на добавление отзыва."""

        response = self.client.post(
            self.url,
            {
                'product': self.product,
                'author': self.user,
                'content': 'test'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
