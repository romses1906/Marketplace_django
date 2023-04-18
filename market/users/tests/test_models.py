from django.contrib.auth import get_user_model
from django.test import TestCase


class UsersModelTests(TestCase):
    """Тестирование модели User."""

    @classmethod
    def setUpClass(cls):
        """Добавление параметров в тест."""
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(email='test@test.ru', password='test')

    def test_create_user(self):
        """Проверка на добавление пользователя."""
        self.assertEqual(self.user.email, 'test@test.ru')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    @classmethod
    def tearDownClass(cls):
        """Удаление тестового пользователя."""
        cls.user.delete()


class UsersFixturesTests(TestCase):
    """Тестирование фикстур."""
    fixtures = ['users.json']

    def test_create_user(self):
        """Сравнение кол-ва пользователей в фикстурах с добавленными в модель."""
        user = get_user_model()
        self.assertEqual(user.objects.count(), 10)
