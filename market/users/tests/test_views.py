from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse

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
            'login': 'test@test.ru',
            'pass': 'test@test.ru'
        }

    def test_register_user(self):
        """Проверка запроса на регистрацию пользователя."""
        response = self.client.post(
            self.url,
            self.data,
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


# class SetNewPasswordViewTests(TestCase):
#     """Тестирование представления смены пароля пользователя."""
#
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(email='test@test.ru', password='test')
#         self.uid = urlsafe_base64_encode(str(self.user.pk).encode())
#         self.token = default_token_generator.make_token(self.user)
#         self.url = reverse('users:set_new_password',  kwargs={
#             'uidb64': self.uid,
#             'token': self.token
#         })
#         self.data = {
#             'new_password1': 'newtest',
#             'new_password2': 'newtest',
#         }
#
#     def test_set_password_user(self):
#         """Проверка установки нового пароля."""
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 302)
#         response = self.client.get(f'/users/set_new_password/{self.uid}/set-password/')
#         self.assertEqual(response.status_code, 200)
#
#         session = self.client.session
#         session['_password_reset_token'] = self.token
#         session.save()
#
#         self.client.post(f'/users/set_new_password/{self.uid}/set_password/', self.data)
#         # self.assertRedirects(response, reverse('users:login_user'))
#         # self.assertEqual(response.status_code, 302)
#         self.assertIsNone(authenticate(email=self.user.email, password='test'))
#         self.assertTrue(authenticate(email=self.user.email, password='newtest'))
#
#     def test_used_template(self):
#         """Тестирование используемого шаблона."""
#         response = self.client.get(reverse('users:set_new_password', args=('uidb64', 'token')))
#         self.assertTemplateUsed(response, 'users/password.j2')
