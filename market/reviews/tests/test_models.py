from django.test import TestCase
from reviews.models import Reviews


class ReviewsFixturesTests(TestCase):
    """Тестирование добавления фикстуры отзывов."""
    fixtures = [
        'users.json',
        'shops.json',
        'categories.json',
        'products.json',
        'offers.json',
        'reviews_product.json'
    ]

    def test_create_reviews(self):
        self.assertEqual(Reviews.objects.count(), 1)
