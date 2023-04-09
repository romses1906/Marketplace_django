from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
	"""Абстрактная модель User, добавляет в стандартную модель дополнительные поля."""
	surname = models.CharField(max_length=50, blank=False, null=False, verbose_name=_('отчество'))
	phone_number = PhoneNumberField(unique=True, null=True, blank=True, verbose_name=_('номер телефона'))
	photo = models.ImageField(upload_to='users_foto/', null = True, blank = True, verbose_name=_('фотография'))
	part_id = models.ForeignKey('Part', null=True, blank=True, on_delete=models.PROTECT, verbose_name=_('роль'))

	class Meta:
		verbose_name = _('пользователь')
		verbose_name_plural = _('пользователи')
		ordering = '-is_superuser', '-date_joined', '-is_active'

	def __str__(self):
		return self.username


class Part(models.Model):
	"""Роли, определяющие пользователей при регистрации."""
	part_name = models.CharField(max_length=100, null=False, blank=False, verbose_name=_('название роли'))

	class Meta:
		verbose_name = _('роль')
		verbose_name_plural = _('роли')

	def __str__(self):
		return self.part_name
