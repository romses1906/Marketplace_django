from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import validate_email
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from shops.models import Shop
from users.models import User


def change_profile(request: HttpRequest, user: QuerySet):
    """Функция принимающая данные метода POST на странице профиля пользователя и вносящая изменение в модель User."""

    # изменение ФИО
    if request.POST.get('name'):
        data = request.POST.get('name').split()
        user.update(
            last_name=data[0],
            first_name=data[1],
            surname=data[2]
        )

    # изменение номера телефона
    if request.POST.get('phone'):
        phone = request.POST.get('phone')
        user.update(
            phone_number=phone
        )

    # изменение аватарки
    if request.FILES:
        file = request.FILES['avatar']
        fail_system = FileSystemStorage()
        filename = fail_system.save(file.name, file)
        user.update(
            photo=filename
        )

    # изменение электронной почты
    if request.POST.get('mail'):
        email = request.POST.get('mail')
        try:
            validate_email(email)
            user.update(
                email=email
            )

            password = user.values('password')[0].get('password')
            user_login = authenticate(email=email, password=password)
            login(request, user_login)
        except ValidationError:
            messages.add_message(request, messages.INFO, _('Email не соответствует требованиям!'))

    # изменение пароля
    if request.POST.get('password') and request.POST.get('passwordReply'):
        password1 = request.POST.get('password')
        password2 = request.POST.get('passwordReply')
        if password1 == password2:
            user.update(
                password=make_password(password1)
            )
            email = user.values('email')[0].get('email')
            user_login = authenticate(email=email, password=password1)
            login(request, user_login)
        else:
            messages.add_message(request, messages.INFO, _('Пароли не совпадают!'))


def create_shop(request: HttpRequest):
    """Добавление магазина в БД."""
    name = request.POST.get('name')
    description = request.POST.get('description')
    phone_number = request.POST.get('phone')
    address = request.POST.get('address')
    email = request.POST.get('mail')
    user = User.objects.get(pk=request.user.pk)

    if Shop.objects.filter(user_id=user.pk).exists():
        return _('Регистрация возможна только одного магазина!')

    Shop.objects.create(
        name=name,
        description=description,
        phone_number=phone_number,
        address=address,
        email=email,
        user=user
    )
    group = Group.objects.get(name='seller')
    user.groups.add(group)
    return _('Магазин успешно добавлен!')


def update_shop(request: HttpRequest):
    """Редактирование магазина."""
    # изменение наименования магазина
    if request.POST.get('name'):
        Shop.objects.filter(user_id=request.user.pk).update(
            name=request.POST.get('name')
        )
    # изменение описания магазина
    if request.POST.get('description'):
        Shop.objects.filter(user_id=request.user.pk).update(
            description=request.POST.get('description')
        )
    # изменение номера телефона магазина
    if request.POST.get('phone'):
        Shop.objects.filter(user_id=request.user.pk).update(
            phone_number=request.POST.get('phone')
        )
    # изменение адреса магазина
    if request.POST.get('address'):
        Shop.objects.filter(user_id=request.user.pk).update(
            address=request.POST.get('address')
        )
    # изменение электронной почты магазина
    if request.POST.get('mail'):
        email = request.POST.get('mail')
        try:
            validate_email(email)
            Shop.objects.filter(user_id=request.user.pk).update(
                email=request.POST.get('mail')
            )
        except ValidationError:
            messages.add_message(request, messages.INFO, _('Email не соответствует требованиям!'))
