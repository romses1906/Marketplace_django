from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist

from .models import User
from .forms import CustomUserCreationForm


class LoginUserView(LoginView):
    """Аутентификация пользователя"""
    template_name = 'users/login.html'


class RegisterView(SuccessMessageMixin, CreateView):
    """
    Регистрация пользователя. При методе POST, функция сохраняет полученные данные в кастомной модели User.
    """
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    queryset = User.objects.all()
    success_url = reverse_lazy('users:register_user')

    def get_success_url(self):
        """
        Метод класса, возвращающий URl.
        """
        return self.success_url

    def form_valid(self, form):
        """
        После регистрации, пользователю добавляется группа с разрешениями "покупатель".
        """
        email = form.cleaned_data.get('email')

        try:
            with transaction.atomic():
                form.save()
                group = Group.objects.get(name='buyer')
                user = User.objects.get(email=email)
                user.groups.add(group)
                messages.add_message(self.request, messages.INFO, _('Вы успешно зарегистрированы!'))
                return HttpResponseRedirect(self.get_success_url())
        except ObjectDoesNotExist:
            messages.add_message(self.request, messages.INFO, _('К сожалению запрос не удался, попробуйте позже!'))
            return HttpResponseRedirect(self.get_success_url())


class PasswordResetRequestView(PasswordResetView):
    """
    Представление по сбросу пароля по почте
    """
    template_name = 'users/e-mail.html'
    success_url = reverse_lazy('users:password_reset')
    subject_template_name = 'users/email/password_subject_reset_mail.txt'
    email_template_name = 'users/email/password_reset_mail.html'


class SetNewPasswordView(PasswordResetConfirmView):
    """
    Представление установки нового пароля
    """
    template_name = 'users/password.html'
    success_url = reverse_lazy('users:login_user')
