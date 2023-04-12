from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    """Абстрактная модель User, добавляет в стандартную модель дополнительные поля."""
    email = models.EmailField(unique=True, verbose_name=_('Электронная почта'))
    surname = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('отчество'))
    phone_number = PhoneNumberField(unique=True, null=True, blank=True, verbose_name=_('номер телефона'))
    photo = models.ImageField(upload_to='users_foto/', null=True, blank=True, verbose_name=_('фотография'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')
        ordering = '-is_superuser', '-date_joined', '-is_active'

    def __str__(self):
        return self.username
