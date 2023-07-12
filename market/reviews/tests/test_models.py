import json

from django.test import TestCase
from reviews.models import Reviews


class ReviewsFixturesTests(TestCase):
    """Тестирование добавления фикстуры отзывов."""
    fixtures = [
        '004_groups.json',
        '005_users.json',
        '010_shops.json',
        '015_categories.json',
        '020_products.json',
        '045_reviews_product.json'
    ]

    def test_create_reviews(self):
        """Проверка кол-во записей в БД."""

        with open('fixtures/045_reviews_product.json', 'r', encoding='utf-8') as file:
            num_reviews = len(json.load(file))

        self.assertEqual(Reviews.objects.count(), num_reviews)
