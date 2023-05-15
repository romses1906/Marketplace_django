import os

from celery import shared_task

from imports import services


@shared_task(name="Импорт товаров")
def imports_all_files_task(*args, **kwargs):
    """Задача на импорт всех файлов в директории `loaded`."""
    module_dir = os.path.dirname(__file__)
    dirs = os.listdir(os.path.join(module_dir, 'files', 'loaded'))
    if len(dirs) > 0:
        for file_name in dirs:
            services.imports(file_name=file_name)

            return 'Импорт завершён'
    else:
        return 'Файлов для импорта нет'
