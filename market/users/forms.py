from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма для регистрации пользователя, с кастомной моделью User."""

    class Meta:
        """Класс, определяющий некоторые параметры формы."""
        model = User
        fields = _('first_name'), _('email'), _('password1'), _('password2')
