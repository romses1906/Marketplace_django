from django.contrib.auth.forms import forms
from shops.models import Shop


class CreateShopForms(forms.ModelForm):
    """Форма регистрации магазина."""
    class Meta:
        model = Shop
        fields = 'name', 'description', 'phone_number', 'address', 'email', 'user',
