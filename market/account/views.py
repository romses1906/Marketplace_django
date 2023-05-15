from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, UpdateView, CreateView

from shops.models import Shop
from users.models import User
from .services import change_profile, create_shop, update_shop


class AccountUser(DetailView):
    """Представления для отображения информации о пользователе на странице аккаунта. """

    template_name = 'account/account.j2'
    context_object_name = 'user'
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(pk=self.request.user.pk)
        if hasattr(user, 'shop'):
            context['shop'] = True
            return context
        context['shop'] = False
        return context


class ProfileUser(SuccessMessageMixin, UpdateView):
    """Представления для редактирования профиля пользователя. """

    template_name = 'account/profile.j2'
    fields = '__all__'
    context_object_name = 'user'

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse_lazy('account:profile_user', kwargs={'pk': self.kwargs['pk']})

    def get_queryset(self):
        """Queryset модели пользователя."""
        user = User.objects.filter(pk=self.request.user.pk)
        return user

    def post(self, request, *args, **kwargs):
        """Метод изменения данных пользователя."""
        change_profile(request, self.get_queryset())

        messages.add_message(self.request, messages.INFO, _('Профиль успешно сохранен'))
        return HttpResponseRedirect(self.get_success_url())


class RegShopView(SuccessMessageMixin, CreateView):
    """Представление для регистрации магазина."""

    template_name = 'account/reg_shop.j2'
    fields = '__all__'
    model = Shop

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse_lazy('account:account_user', kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        """Добавление магазина."""
        message = create_shop(request=request)

        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())


class UpdateShopView(SuccessMessageMixin, UpdateView):
    """Представление для редактирования магазина."""

    template_name = 'account/update_shop.j2'
    fields = '__all__'
    context_object_name = 'shop'
    model = Shop

    def get_object(self, queryset=None):
        """Возвращение объекта магазина."""
        return get_object_or_404(Shop, user_id=self.kwargs.get('pk'))

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse_lazy('account:update_shop', kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        """Редактирование магазина."""
        update_shop(request=request)
        messages.add_message(self.request, messages.INFO, _('Магазин успешно редактирован'))
        return HttpResponseRedirect(self.get_success_url())
