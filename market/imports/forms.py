from django import forms


class UploadFileForm(forms.Form):
    """Форма добавления файлов."""
    file = forms.FileField()
