import json
import logging
import os
import shutil
from datetime import datetime

from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.db.models import F
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _

from config.settings import RECIPIENTS_EMAIL, DEFAULT_FROM_EMAIL
from products.models import Product
from shops.models import Shop, Offer
from users.models import User


def save_file(file, username) -> str:
    """Загрузка файла импорта в директории ожидания."""
    file_sys = FileSystemStorage(location='imports/files/loaded/')
    date = datetime.now().strftime("%d-%m-%Y_%H.%M.%S")
    file_name = f'({date})-{username}-{file.name}'
    file_sys.save(file_name, file)
    return _("Файл загружен и ожидает импорта!")


def logging_info(file_name: str):
    """Настройки логирования для импорта."""
    logger = logging.getLogger(f'{file_name}')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(f'imports/files/logs/{file_name}.log', encoding='utf-8')
    formatter = logging.Formatter('[%(asctime)s] - [%(levelname)s] - [%(message)s]')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def imports(file_name: str):
    """Загрузка данных в БД."""
    logger = logging_info(file_name)
    logger.info(f'Начало импорта {file_name}')

    file_path = os.path.join(os.path.dirname(__file__), 'files', 'loaded', file_name)
    username = file_name.split('-')[3]
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data_list = json.load(file)
            user = User.objects.get(username=username)
            shop = Shop.objects.get(user_id=user.pk)

            for data in data_list:
                # проверка заполнения полей
                if not data['name']:
                    raise KeyError
                if not data['in_stock']:
                    raise KeyError
                if not data['price']:
                    raise KeyError

                else:
                    if Product.objects.filter(name=data['name']).exists():
                        product = Product.objects.get(name=data['name'])
                    else:
                        raise IntegrityError(f'Товара с наименованием `{data["name"]}` не существует!')

                    if Offer.objects.filter(shop=shop).filter(product=product).exists():
                        Offer.objects.filter(shop=shop).filter(product=product).update(
                            price=float(data['price']),
                            in_stock=F('in_stock') + int(data['in_stock'])
                        )
                        logger.info(f'Продукт `{data["name"]}` обновлён')
                    else:
                        Offer.objects.update_or_create(
                            shop=shop,
                            product=product,
                            in_stock=int(data['in_stock']),
                            price=float(data['price'])
                        )
                        logger.info(f'Продукт `{data["name"]}` добавлен')

        file_new_path = os.path.join(os.path.dirname(__file__), 'files', 'completed')
        shutil.move(file_path, file_new_path)
    except IntegrityError as ex:
        logger.warning(ex)
        file_new_path = os.path.join(os.path.dirname(__file__), 'files', 'failed_imports')
        shutil.move(file_path, file_new_path)
    except KeyError as ex:
        logger.warning(f'Поле {ex} не заполнено!')
        file_new_path = os.path.join(os.path.dirname(__file__), 'files', 'failed_imports')
        shutil.move(file_path, file_new_path)
    logger.info(f'Окончание импорта {file_name}')

    # отправка сообщения о проведённом импорте
    from_email = User.objects.get(username=username).email
    date = datetime.now().strftime("%d-%m-%Y_%H.%M.%S")
    message = f'{date} был проведён импорт товаров из {file_name}. '

    send_mail(f'Проведение импорта от {from_email}', message, DEFAULT_FROM_EMAIL, RECIPIENTS_EMAIL)


def imports_all_files():
    """Импорт всех файлов в директории."""
    module_dir = os.path.dirname(__file__)
    dirs = os.listdir(os.path.join(module_dir, 'files', 'loaded'))
    for file_name in dirs:
        imports(file_name=file_name)


def import_file(file_name: str):
    """Импорт запрошенного файла."""
    name = "".join(file_name)
    imports(file_name=name)


def import_files(files: list):
    """Импорт запрошенных файлов."""
    for file_name in files:
        imports(file_name=file_name)
