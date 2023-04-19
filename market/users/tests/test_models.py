from django.contrib.auth import get_user_model
from django.test import TestCase


class UsersModelTests(TestCase):

    @classmethod
    def setUpClass(cls):

        user_model = get_user_model()
        cls.user = user_model.objects.create_user(email='test@test.ru', password='test')

    def test_create_user(self):

        self.assertEqual(self.user.email, 'test@test.ru')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()


class UsersFixturesTests(TestCase):
    fixtures = ['005_users.json']

    def test_create_user(self):
        user = get_user_model()
        self.assertEqual(user.objects.count(), 10)
