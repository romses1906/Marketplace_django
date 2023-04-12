from django.contrib.auth import get_user_model
from django.test import TestCase


class UsersModelTests(TestCase):
    def test_create_user(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username='test', email='test@test.ru', password='test')
        self.assertEqual(user.email, 'test@test.ru')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
