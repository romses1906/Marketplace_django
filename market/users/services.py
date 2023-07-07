from users.models import User


def create_user(password, user_data):
    """Функция принимающая данные метода POST на странице оформления заказа и созадющая User."""

    try:
        last_name, first_name, surname = user_data['full_name'].split(' ')
    except ValueError:
        last_name, first_name, surname = user_data['full_name'], '', ''

    User.objects.create_user(
        email=user_data['email'],
        password=password,
        last_name=last_name,
        first_name=first_name,
        surname=surname,
        phone_number=user_data['phone_number']
        )


def normalize_email(email):
    """
    Нормализует адрес электронной почты, указав в нижнем регистре его доменную часть.
    """
    email = email or ""
    try:
        email_name, domain_part = email.strip().rsplit("@", 1)
    except ValueError:
        pass
    else:
        email = email_name + "@" + domain_part.lower()
    return email
