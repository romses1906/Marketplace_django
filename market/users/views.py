from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from .models import User
from .forms import CustomUserCreationForm


class LoginUserView(LoginView):
    """Аутентификация пользователя"""
    template_name = 'users/login.html'


class RegisterView(CreateView):
    """
    Регистрация пользователя. При методе POST, функция сохраняет полученные данные в кастомной модели User.
    """
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    queryset = User.objects.all()

    def form_valid(self, form):
        """
        После регистрации, пользователь аутентифицируется и переадресовывается на главную страницу.
        А также добавляется группа с разрешениями "покупатель".
        """
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        try:
            with transaction.atomic():
                form.save()
                user = authenticate(email=email, password=password)
                login(self.request, user)
                group = Group.objects.get(name='buyer')
                user = User.objects.get(email=email)
                user.groups.add(group)
                return redirect('/')
        except Exception:
            return HttpResponse(_('К сожалению запрос не удался, попробуйте позже!'))


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
