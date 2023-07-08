from django.contrib.auth import password_validation, get_user_model
from django.contrib.auth.forms import SetPasswordForm, forms, UserCreationForm
from django.utils.translation import gettext_lazy as _


class SignUpUserForm(UserCreationForm):
    """Кастомная форма регистрации."""
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'username',
                'placeholder': _('имя пользователя'),
            },
        ),
    )
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                'autocomplete': 'email',
                'placeholder': 'email',
            },
        ),
    )
    password1 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                'placeholder': _('пароль'),
            }
        ),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                'placeholder': _('повторите пароль'),
            }
        ),
        help_text=password_validation.password_validators_help_text_html(),
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email',)


class CustomSetPasswordForm(SetPasswordForm):
    """Кастомная форма установки нового пароля."""

    new_password1 = forms.CharField(
        label=_('Новый пароль'),
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                'placeholder': _('новый пароль'),
            },
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_('Повторите новый пароль'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                'placeholder': _('повторите новый пароль'),
            },
        ),
    )
