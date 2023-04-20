from django.contrib.auth import get_user_model
from django.test import TestCase


class UsersModelTests(TestCase):
    """Тестовый класс проверки пользовательской модели"""

    @classmethod
    def setUpClass(cls):
        """Создает фикстуру пользователя."""
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(email='test@test.ru', password='test')

    def test_create_user(self):
        """Проверяет атрибуьы фикстурного пользователя в базе данных"""
        self.assertEqual(self.user.email, 'test@test.ru')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    @classmethod
    def tearDownClass(cls):
        """Удаляет фикстурного пользователя."""
        cls.user.delete()


class UsersFixturesTests(TestCase):
    """Тестовый класс проверки файла с фикстурами пользователя."""
    fixtures = ['005_users.json']

    def test_create_user(self):
        """Проверяет, все ли пользователи из файла с фикстурами загружены."""
        user = get_user_model()
        self.assertEqual(user.objects.count(), 10)
