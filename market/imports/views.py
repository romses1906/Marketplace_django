from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from .forms import UploadFileForm
from .services import save_file


class FileUploadView(SuccessMessageMixin, FormView):
    """Представления для загрузки файла с продуктами от продавца."""
    form_class = UploadFileForm
    template_name = 'imports/imports.j2'

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse_lazy('account:account_user', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        """Обработка формы и сохранение загруженного файла."""
        file = form.cleaned_data.get('file')
        if file.name.lower().endswith('.json'):
            username = self.request.user.username
            save_info = save_file(file=file, username=username)
            messages.add_message(
                self.request, messages.INFO, save_info)
            return HttpResponseRedirect(self.get_success_url())

        messages.add_message(
            self.request, messages.INFO, _('Неверный формат файла.'))
        return HttpResponseRedirect(reverse('imports:upload_file', kwargs={'pk': self.kwargs['pk']}))
