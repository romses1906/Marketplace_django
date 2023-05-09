from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, UpdateView

from users.models import User
from .services import change_profile


class AccountUser(DetailView):
    """Представления для отображения информации о пользователе на странице аккаунта. """

    template_name = 'account/account.j2'
    queryset = User.objects.all()
    context_object_name = 'user'


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
