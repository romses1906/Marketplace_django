from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма для регистрации пользователя, с кастомной моделью User."""

    class Meta:
        """Класс, определяющий некоторые параметры формы."""
        model = User
        fields = 'first_name', 'email', 'password1', 'password2'
