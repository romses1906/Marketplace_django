from django.contrib.auth import authenticate, login

from users.models import User


def create_user(request, user_data):
    """Функция принимающая данные метода POST на странице оформления заказа и созадющая User."""

    password = request.POST.get('password')
    last_name, first_name, surname = user_data['full_name'].split(' ')
    # Регистрация пользователя
    new_user = User.objects.create_user(
        email=user_data['email'],
        password=password,
        last_name=last_name,
        first_name=first_name,
        surname=surname,
        phone_number=user_data['phone_number']
    )
    # Авторизация пользователя
    authenticated_user = authenticate(request, email=user_data['email'], password=password)
    if authenticated_user is not None:
        login(request, authenticated_user)
    else:
        print('Authentication failed')
    return new_user
