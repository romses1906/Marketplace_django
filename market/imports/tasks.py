import os

from celery import shared_task

from config.settings import CELERY_TASK_NAME_1
from imports.services import Imports


@shared_task(name=CELERY_TASK_NAME_1)
def imports_all_files_task(*args, **kwargs):
    """Задача на импорт всех файлов в директории `loaded`."""
    imports = Imports()
    module_dir = os.path.dirname(__file__)
    dirs = os.listdir(os.path.join(module_dir, 'files', 'loaded'))
    if len(dirs) > 0:
        for file_name in dirs:
            imports.process_imports(file_name=file_name)
            return 'Импорт завершён'
    else:
        return 'Файлов для импорта нет'
