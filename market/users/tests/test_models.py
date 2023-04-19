from django.contrib.auth import get_user_model
from django.test import TestCase


class UsersModelTests(TestCase):
    """Test model User."""

    @classmethod
    def setUpClass(cls):
        """Добавление атрибутов класса."""
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(email='test@test.ru', password='test')

    def test_create_user(self):
        """Проверка добавленного пользователя."""
        self.assertEqual(self.user.email, 'test@test.ru')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    @classmethod
    def tearDownClass(cls):
        """Удаление пользователя из базы."""
        cls.user.delete()


class UsersFixturesTests(TestCase):
    """Тестирование фикстуры."""
    fixtures = ['005_users.json']

    def test_create_user(self):
        """Проверка кол-ва добавленных пользователей из фикстуры."""
        user = get_user_model()
        self.assertEqual(user.objects.count(), 10)
