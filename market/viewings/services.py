from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import validate_email
from django.http import QueryDict
from django.utils.translation import gettext as _

from users.models import User


def change_profile(data: QueryDict, user_id, file=None):
    """Функция принимающая данные метода POST на странице профиля пользователя и вносящая изменение в модель User."""
    user = User.objects.filter(pk=user_id)

    # изменение ФИО
    if data.get('name'):
        name = data.get('name').split()
        user.update(
            last_name=name[0],
            first_name=name[1],
            surname=name[2]
        )

    # изменение номера телефона
    if data.get('phone'):
        user.update(
            phone_number=data.get('phone')
        )

    # изменение аватарки
    if file:
        fail_system = FileSystemStorage()
        filename = fail_system.save(file.name, file)
        user.update(
            photo=filename
        )

    # изменение электронной почты
    if data.get('mail'):
        email = data.get('mail')
        try:
            validate_email(email)
            user.update(
                email=email
            )
        except ValidationError:
            return _('Email не соответствует требованиям!')

    # изменение пароля
    if data.get('password') and data.get('passwordReply'):
        password1 = data.get('password')
        password2 = data.get('passwordReply')
        if password1 == password2:
            user.update(
                password=make_password(password1)
            )
        else:
            return _('Пароли не совпадают!')
    return _('Профиль успешно изменён.')
