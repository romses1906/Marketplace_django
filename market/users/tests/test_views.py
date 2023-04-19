from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class LoginViewTests(TestCase):
    """Тестирование представления аутентификации пользователя."""

    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(email='test@test.ru', password='test')
        self.url = reverse('users:login_user')
        self.response = self.client.get(self.url)

    def test_login(self):
        """Тестирование аутентификации пользователя."""
        response = self.client.post(
            self.url,
            {
                'email': self.user.email,
                'password': self.user.password
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_used_template(self):
        """Тестирование используемого шаблона."""
        self.assertTemplateUsed(self.response, 'users/login.html')


class RegisterViewTests(TestCase):
    """Тестирование представления регистрации пользователя."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:register_user')
        self.response = self.client.get(self.url)

    def test_register_user(self):
        """Проверка запроса на регистрацию пользователя."""
        response = self.client.post(
            self.url,
            {
                'email': 'test@test.ru',
                'password': 'test'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_used_template(self):
        """Тестирование используемого шаблона."""
        self.assertTemplateUsed(self.response, 'users/register.html')


class ResetPasswordViewTests(TestCase):
    """Тестирование представления сброса пароля пользователя."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:password_reset')
        self.response = self.client.get(self.url)

    def test_reset_password_user(self):
        """Проверка запроса на сброс пароля."""
        response = self.client.post(
            self.url,
            {
                'email': 'test@test.ru',
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_used_template(self):
        """Тестирование используемого шаблона."""
        self.assertTemplateUsed(self.response, 'users/e-mail.html')


class SetNewPasswordViewTests(TestCase):
    """Тестирование представления смены пароля пользователя."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:set_new_password', args=('uidb64', 'token'))
        self.response = self.client.get(self.url)

    def test_set_password_user(self):
        """Проверка установки нового пароля."""
        response = self.client.post(
            self.url,
            {
                'email': 'test@test.ru',
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_used_template(self):
        """Тестирование используемого шаблона."""
        self.assertTemplateUsed(self.response, 'users/password.html')
