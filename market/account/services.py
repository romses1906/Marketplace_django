from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import validate_email
from django.http import QueryDict
from django.utils.translation import gettext as _

from shops.models import Shop
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


class ShopManager:
    """Класс для добавления или редактирования магазина."""

    def __init__(self, data, user_pk):
        """Инициализация класса."""
        self.name = data.get('name')
        self.description = data.get('description')
        self.phone_number = data.get('phone')
        self.address = data.get('address')
        self.email = data.get('mail')
        self.user = User.objects.get(pk=user_pk)

    def create(self):
        """Добавление магазина."""
        Shop.objects.create(
            name=self.name,
            description=self.description,
            phone_number=self.phone_number,
            address=self.address,
            email=self.email,
            user=self.user
        )
        group = Group.objects.get(name='seller')
        self.user.groups.add(group)
        return _('Магазин успешно добавлен!')

    def update(self):
        """Редактирование магазина."""
        try:
            validate_email(self.email)
            Shop.objects.filter(user_id=self.user).update(
                name=self.name,
                email=self.email,
                description=self.description,
                phone_number=self.phone_number,
                address=self.address
            )
        except ValidationError:
            return _('Email не соответствует требованиям!')
        return _('Магазин успешно редактирован')
