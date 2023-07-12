from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView

from orders.models import Order
from shops.models import Shop
from users.models import User
from viewings.models import HistorySearch
from .forms import CreateShopForms
from .services import change_profile


class AccountUser(DetailView):
    """Представления для отображения информации о пользователе на странице аккаунта."""
    template_name = 'viewings/account.j2'
    context_object_name = 'user'
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(pk=self.request.user.pk)
        context['last_order'] = Order.objects.select_related('user').filter(user=self.request.user).last()
        if HistorySearch.objects.filter(user=self.request.user).exists():
            context['history'] = HistorySearch.objects.get(user=self.request.user)
        if hasattr(user, 'shop'):
            context['shop'] = True
            return context
        context['shop'] = False
        return context


class ProfileUser(LoginRequiredMixin, SuccessMessageMixin, View):
    """Представления для редактирования профиля пользователя."""
    template_name = 'viewings/profile.j2'

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse('account:profile_user', kwargs={'pk': self.kwargs['pk']})

    def get_queryset(self):
        """Queryset модели пользователя."""
        return get_object_or_404(User, pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        """Получение страницы для редактирования профиля."""
        context = {
            'user': self.get_queryset()
        }
        return render(self.request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        """Метод изменения данных пользователя."""
        data = self.request.POST

        if self.request.FILES:
            file = self.request.FILES['avatar']
            info = change_profile(data=data, user_id=self.request.user.pk, file=file)
        else:
            info = change_profile(data=data, user_id=self.request.user.pk)

        messages.add_message(self.request, messages.INFO, info)
        return HttpResponseRedirect(self.get_success_url())


class RegShopView(SuccessMessageMixin, CreateView):
    """Представление для регистрации магазина."""
    template_name = 'viewings/reg_shop.j2'
    model = Shop
    success_message = _('Магазин успешно добавлен!')
    form_class = CreateShopForms

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse('account:account_user', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        """Перед сохранением формы добавляем пользователя."""
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)


class UpdateShopView(SuccessMessageMixin, UpdateView):
    """Представление для редактирования магазина."""
    template_name = 'viewings/update_shop.j2'
    fields = 'name', 'description', 'phone_number', 'address', 'email',
    success_message = _('Магазин успешно редактирован')

    def get_object(self, queryset=None):
        """Возвращение объекта магазина."""
        return get_object_or_404(Shop, user_id=self.kwargs.get('pk'))

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse_lazy('account:update_shop', kwargs={'pk': self.kwargs['pk']})
