from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode

from users.models import User


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
        self.assertTemplateUsed(self.response, 'users/login.j2')


class RegisterViewTests(TestCase):
    """Тестирование представления регистрации пользователя."""
    fixtures = [
        '004_groups.json',
    ]

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:register_user')
        self.response = self.client.get(self.url)
        self.data = {
            'username': 'test',
            'email': 'test@test.ru',
            'password1': 'test@test.ru',
            'password2': 'test@test.ru',
        }

    def test_register_user(self):
        """Проверка запроса на регистрацию пользователя."""
        response = self.client.post(
            self.url,
            {
                'username': 'test',
                'email': 'test@test.ru',
                'password1': 'testpassword',
                'password2': 'testpassword',
            },
        )
        user_count = User.objects.count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user_count, 1)

    def test_used_template(self):
        """Тестирование используемого шаблона."""
        self.assertTemplateUsed(self.response, 'users/register.j2')


class ResetPasswordViewTests(TestCase):
    """Тестирование представления сброса пароля пользователя."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:password_reset')
        self.response = self.client.get(self.url)
        user_model = get_user_model()
        self.user = user_model.objects.create_user(email='test@test.ru', password='test@test.ru')

    def test_reset_password_user(self):
        """Проверка запроса на сброс пароля."""
        response = self.client.post(
            self.url,
            {
                'email': self.user.email,
            },

        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

    def test_used_template(self):
        """Тестирование используемого шаблона."""
        self.assertTemplateUsed(self.response, 'users/e-mail.j2')


class SetNewPasswordViewTests(TestCase):
    """Тестирование представления смены пароля пользователя."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@test.ru', password='test')
        self.uid = urlsafe_base64_encode(str(self.user.pk).encode())
        self.token = PasswordResetTokenGenerator().make_token(self.user)
        self.url = reverse('users:set_new_password',  args={'uidb64', 'token'})
        self.response = self.client.get(self.url)

    def test_set_password_user(self):
        """Проверка установки нового пароля."""
        url = f"/users/set_new_password/{self.uid}/set-password/"
        self.client.get(url)
        # сохраняем токен в сессии
        session = self.client.session
        session['_password_reset_token'] = self.token
        session.save()
        # данные нового пароля
        valid_data = {
            "new_password1": "I_like_bagels_100",
            "new_password2": "I_like_bagels_100"
        }
        # запрос на установку нового пароля
        response = self.client.post(url, valid_data)
        # проверка перенаправления пользователя на страницу входа
        self.assertRedirects(response, reverse("users:login_user"))
        # проверяем что пароль действительно сменился
        self.assertFalse(authenticate(email=self.user.email, password='test'))
        self.assertTrue(authenticate(email=self.user.email, password='I_like_bagels_100'))
        self.assertTrue(self.client.login(email=self.user.email, password='I_like_bagels_100'))

    def test_used_template(self):
        """Тестирование используемого шаблона."""
        self.assertTemplateUsed(self.response, 'users/password.j2')
