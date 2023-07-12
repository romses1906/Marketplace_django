from django import forms

from orders.models import Order


class UserForm(forms.Form):
    """Форма получения данных пользователя оформляющего заказ."""
    full_name = forms.CharField(label='Ф.И.О.', max_length=100, required=True, error_messages={
        'required': 'Поле обязательно для заполнения!.'})
    email = forms.EmailField(label='Email', required=True, error_messages={
        'required': 'Поле обязательно для заполнения!'})
    phone_number = forms.CharField(label='Номер телефона', max_length=20, required=True, error_messages={
        'required': 'Поле обязательно для заполнения!'})


class DeliveryForm(forms.Form):
    """Форма получения данных о способе доставки заказа."""
    DELIVERY_OPTIONS = (
        ('Delivery', 'Обычная доставка'),
        ('Express Delivery', 'Экспресс-доставка')
    )

    delivery_option = forms.ChoiceField(choices=DELIVERY_OPTIONS, label='Способ доставки')
    delivery_address = forms.CharField(label='Адрес', max_length=100, required=True)
    delivery_city = forms.CharField(label='Город', max_length=100, required=True)


class PaymentForm(forms.Form):
    """Форма получения данных о способе оплаты заказа."""
    PAYMENT_OPTIONS = (
        ('Online Card', 'Онлайн-картой'),
        ('Another card', 'Оплата чужой картой')
    )

    payment_option = forms.ChoiceField(choices=PAYMENT_OPTIONS, label='Способ оплаты')


class CommentForm(forms.ModelForm):
    """Форма получения данных по заказу и комментария пользователя."""
    comment = forms.CharField(label='Комментарий', required=False, widget=forms.Textarea)

    class Meta:
        model = Order
        fields = ('comment',)
