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
        '030_offers.json',
        '045_reviews_product.json'
    ]

    def test_create_reviews(self):
        """Проверка кол-во записей в БД."""
        self.assertEqual(Reviews.objects.count(), 1)
