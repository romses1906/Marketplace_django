# Маркетплейс MEGANO
Интернет-магазин, являющийся агрегатором товаров различных продавцов.

## Как установить
Для работы микросервиса нужен Python версии не ниже 3.10 и установленное ПО для контейнеризации - [Docker](https://docs.docker.com/engine/install/). 

Склонируйте репозиторий
```shell
git clone git@github.com:romses1906/Marketplace_django.git
``` 

Настройка переменных окружения  

Создайте файл .env и заполните его по примеру env.dist:  
```yaml
DATABASE_URL = postgresql://pg_user:secret@127.0.0.1:5434/market
REDIS_URL = redis://127.0.0.1:6379/0
```

Запуск СУБД Postgresql
```shell
docker run --name market-db -e POSTGRES_USER=pg_user -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=market -p 5434:5432 -d postgres
```
Запуск брокера сообщений REDIS
```shell
docker run --name redis-db -p 6379:6379 -d redis 
```
Установка виртуального окружения для среды разработки на примере ОС Windows
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements\dev.txt
```
Установка виртуального окружения для продовой среды на примере ОС Linux
```shell
python -m venv venv
. venv/bin/activate
pip install -r requirements/base.txt
```  
### Как удалить контейнеры
СУБД Postgres  
```
 docker rm -f -v market-db
```

Брокер сообщений REDIS  
```
 docker rm -f -v redis-db
```

## Проверка форматирования кода
Проверка кода выполняется из корневой папки репозитория.    
* Анализатор кода flake8  
```shell
flake8
```
* Линтер pylint  
```shell
pylint --rcfile=.pylintrc market/* 
```

## Как запустить web-сервер
Запуск сервера производится в активированном локальном окружение из папки `market/`
```shell
python manage.py runserver 0.0.0.0:8000
```


## Разработка
### Работа в оболочке
```shell
python manage.py shell_plus
```
### Загрузка фикстур

Загрузка данных в модели проекта (фикстур) выполняется из папки `market/` следующей командой:

```shell
python manage.py loaddata fixtures/*.json
```

#### Данные cуперпользователя:

email: admin@admin.ru password: admin

#### Данные зарегистрированных пользователей:

1. email: david@test.ru password: 1304test
2. email: kevin@test.ru password: 1304test
3. email: robert@test.ru password: 1304test
4. email: skott@test.ru password: 1304test

#### Данные зарегистрированных пользователей, у которых есть магазин:

1. email: kenneth@test.ru password: 1304test
2. email: willard@test.ru password: 1304test
3. email: kyle@test.ru password: 1304test
4. email: glenn@test.ru password: 1304test
5. email: keith@test.ru password: 1304test  


### Приложение imports

Команды для выполнения импорта:

- выполнения импорта всех файлов
````shell
python manage.py imports all
````
- выполнения импорта одного файла
````shell
python manage.py imports <имя файла>
````
- выполнения импорта нескольких файлов
````shell
python manage.py imports <имена файлов через пробел>
````

#### CELERY

Также импорт можно поставить на периодическое выполнение задачи.
Для настройки времени периодов выполнения задач необходимо задать требуемые параметры 
в админ панели, подробнее можно посмотреть в статье [Сергея Климова](https://habr.com/ru/articles/711590/).

Команды запуска выполнения задач в фоновом режиме:

- Запуск брокера сообщений Redis
````shell
redis-server
````
- Запуск Celery для выполнения задачи по импорту
````shell
celery -A config worker -l info
````
- Запускаем службу beat
````shell
celery -A config beat -l info
````
- Запускаем сервер
````shell
python manage.py runserver
````


#### Система оплаты Stripe

Система оплаты настроена на тестовый режим!

Номер карты для тестирования оплаты - 
4242 4242 4242 4242 4242, остальные данные рандомные.

Для доступа к платёжной системе, необходимо зарегистрироваться на сервисе и после получение API ключей добавить в .env:
- STRIPE_SECRET_KEY = секретный ключ
- STRIPE_PUBLISHABLE_KEY = публичный ключ

[![2023-06-15-23-22-56.png](https://i.postimg.cc/nrRkS4vm/2023-06-15-23-22-56.png)](https://postimg.cc/XB5dpy1N)

- STRIPE_WEBHOOK_KEY = ключ веб перехвадчика

Инструкции по настройке и получения ключа webhook можно почитать в официальной документации [сервиса](https://stripe.com/docs/stripe-cli#install)

#### Почта SMPT

Сервис отправки электронных писем настроен на сервере Google:

- EMAIL_HOST_USER = имя пользователя
- EMAIL_HOST_PASSWORD = пароль полученный при оформлении двухэтапной аутентификации
