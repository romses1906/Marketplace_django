from django.test import TestCase, Client
from django.urls import reverse, resolve

from users.views import RegisterView, LoginUserView, PasswordResetRequestView, SetNewPasswordView


class LoginUsersTest(TestCase):
    """ Тестирование URL аутентификации пользователя """

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:login_user')
        self.response = self.client.get(self.url)

    def test_page_uses_the_correct_url(self):
        """Проверка используемого URL."""
        self.assertURLEqual(self.url, '/users/login_user/')

    def test_url_uses_the_desired_view(self):
        """Проверка используемого представления."""
        view = resolve(self.url)
        desired_view = LoginUserView.as_view().__name__
        self.assertEqual(view.func.__name__, desired_view)


class RegisterUsersTest(TestCase):
    """ Тестирование URL регистрации пользователя """

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:register_user')
        self.response = self.client.get(self.url)

    def test_page_uses_the_correct_url(self):
        """Проверка используемого URL."""
        self.assertURLEqual(self.url, '/users/register_user/')

    def test_url_uses_the_desired_view(self):
        """Проверка используемого представления."""
        view = resolve(self.url)
        desired_view = RegisterView.as_view().__name__
        self.assertEqual(view.func.__name__, desired_view)


class ResetPasswordUsersTest(TestCase):
    """ Тестирование URL сброса пароля """

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:password_reset')
        self.response = self.client.get(self.url)

    def test_page_uses_the_correct_url(self):
        """Проверка используемого URL."""
        self.assertURLEqual(self.url, '/users/password_reset/')

    def test_url_uses_the_desired_view(self):
        """Проверка используемого представления."""
        view = resolve(self.url)
        desired_view = PasswordResetRequestView.as_view().__name__
        self.assertEqual(view.func.__name__, desired_view)


class SetNewPasswordUsersTest(TestCase):
    """ Тестирование URL сброса пароля """

    def setUp(self):
        self.client = Client()
        self.url = reverse('users:set_new_password', args=('uidb64', 'token'))
        self.response = self.client.get(self.url)

    def test_page_uses_the_correct_url(self):
        """Проверка используемого URL."""
        self.assertURLEqual(self.url, '/users/set_new_password/uidb64/token/')

    def test_url_uses_the_desired_view(self):
        """Проверка используемого представления."""
        view = resolve(self.url)
        desired_view = SetNewPasswordView.as_view().__name__
        self.assertEqual(view.func.__name__, desired_view)
