from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from .forms import CustomSetPasswordForm, SignUpUserForm


class LoginUserView(SuccessMessageMixin, LoginView):
    """Аутентификация пользователя"""
    template_name = 'users/login.j2'
    success_url = reverse_lazy('shops:home')

    def form_invalid(self, form):
        """Отправляем сообщение пользователю о неверных данных"""
        messages.add_message(
                self.request, messages.INFO, _('Неверный логин или пароль. Проверьте введённые данные'))
        return super().form_invalid(form)


class LogoutUserView(LogoutView):
    """Представления для выхода пользователя из аккаунта."""
    template_name = 'includes/header/wrap.j2'


class RegisterView(SuccessMessageMixin, CreateView):
    """Регистрация пользователя. При методе POST, функция сохраняет полученные данные в кастомной модели User."""
    template_name = 'users/register.j2'
    form_class = SignUpUserForm
    success_url = reverse_lazy('users:login_user')

    def form_valid(self, form):
        """После регистрации, пользователю добавляется группа с разрешениями "покупатель"."""
        user = form.save()
        try:
            with transaction.atomic():
                group = Group.objects.get(name='buyer')
                user.groups.add(group)
                login(self.request, user)
                messages.add_message(
                    self.request, messages.INFO,
                    _('Вы успешно зарегистрированы! Введите пожалуйста ФИО.')
                )
                return HttpResponseRedirect(reverse('account:profile_user', kwargs={'pk': user.pk}))
        except ObjectDoesNotExist:
            messages.add_message(self.request, messages.INFO, _('К сожалению запрос не удался, попробуйте позже!'))
            return HttpResponseRedirect(reverse('users:register_user'))
        except IntegrityError:
            messages.add_message(self.request, messages.INFO, _('Вы уже зарегистрированы!'))
            return HttpResponseRedirect(self.success_url)


class PasswordResetRequestView(SuccessMessageMixin, PasswordResetView):
    """Представление по сбросу пароля по почте."""
    template_name = 'users/e-mail.j2'
    success_url = reverse_lazy('users:password_reset')
    subject_template_name = 'users/email/password_subject_reset_mail.txt'
    email_template_name = 'users/email/password_reset_mail.html'
    success_message = _('Письмо для восстановления пароля отправлено Вам на почту.')


class SetNewPasswordView(SuccessMessageMixin, PasswordResetConfirmView):
    """Представление установки нового пароля."""
    form_class = CustomSetPasswordForm
    template_name = 'users/password.j2'
    success_url = reverse_lazy('users:login_user')
    success_message = _('Пароль успешно изменён')
