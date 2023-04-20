from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import User
from .forms import CustomUserCreationForm


class LoginUserView(LoginView):
    """Аутентификация пользователя"""
    template_name = 'users/login.html'


class RegisterView(CreateView):
    """
    Регистрация пользователя. При методе POST, функция сохраняет полученные данные в кастомной модели User.
    :return: После регистрации, пользователь аутентифицируется и переадресовывается на главную страницу.
    """
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    queryset = User.objects.all()

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = authenticate(email=email, password=password)
        login(self.request, user)
        return redirect('/')


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
