# FOODGFAM
![Deploy badge](https://github.com/Violetta-tsoy/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg) 
##  Описание проекта:

Проект Foodgram, «Продуктовый помощник» включает в себя онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии в проекте
- Python 3.9.10
- Django 3.2
- Django Rest Framework 3.14
- Docker 20.10.24
- Gunicorn 20.0.4
- Nginx 1.21.3

## Инструкции по запуску:
### Локальный запуск проекта:
Установите docker-compose, с этим вам поможет официальная документация: https://docs.docker.com/compose/install/ 

Склонируйте репозиторий:
```
git clone https://github.com/Violetta-tsoy/foodgram-project-react.git
```
Cоздайте и активируйте виртуальное окружение: 
``` 
python -m venv venv 
``` 
``` 
source venv/Scripts/activate
``` 
Установите зависимости из файла requirements.txt: 
``` 
python -m pip install --upgrade pip 
``` 
``` 
pip install -r requirements.txt 
``` 
Перейдите в директорию infra и создайте файл .env с переменными окружения для работы с базой данных. Шаблон наполнения env-файла:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
Из директории infra/ необходимо выполнить команду 
```
docker-compose up -d --build
```
Выполните миграции:
```
docker-compose exec backend python manage.py migrate
```
Создайте суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```
Далее необходимо собрать статику:
```
docker-compose exec backend python manage.py collectstatic --no-input
```
Создайте дамп (резервную копию) базы данных:
```
docker compose exec backend python manage.py dumpdata > fixtures.json
```
Для остановки приложения в контейнерах выполните команду:
```
docker-compose down -v
```
Для заполнения базы данными выполните миграции:
```
python manage.py makemigrations
python manage.py migrate
```
Создайте учетную запись администратора:
```
python manage.py createsuperuser
```
Запустите бекэнд сервер:
```
python manage.py runserver
```
Сайт доступен по адресу:
http://localhost/signin

Адрес для работы с админ панелью:
http://localhost/admin/

Для просмотра документации с примерами перейдите по адресу: http://localhost/api/docs/

### Запуск проекта на удаленном сервере:
Войдите на свой удаленный сервер в облаке.
Остановите службу nginx:
```
sudo systemctl stop nginx 
```
Установите docker:
```
sudo apt install docker.io 
```
Установите docker-compose, с этим вам поможет официальная документация: https://docs.docker.com/compose/install/

Скопируйте файлы docker-compose.yaml и nginx/default.conf из вашего проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно.

Добавьте в Secrets GitHub Actions переменные окружения для работы базы данных.
```
SECRET_KEY=<secret key django проекта>
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_NAME=postgres
DB_PASSWORD=postgres
DB_PORT=5432
DB_USER=postgres

DOCKER_PASSWORD=<Docker password>
DOCKER_USERNAME=<Docker username>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ(cat ~/.ssh/id_rsa)>

TG_CHAT_ID=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
```
### Работа с контейнерами на сервере
Зайдите на ваш сервер ssh your_login@public_ip

Пройдите к директорию, где у вас находится фаил docker-compose.yml и выполните команды:
```
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic --no-input
```
Для заполнения базы данными:
1. Скопируйте папку data на ваш сервер
```
scp -r имя_папки username@public_id:home/username
```
2. Найдите id контейнера backend
```
docker container ls
```
3. Скопируйте папку data в контейнер
```
docker cp data/ <container_id>:data/
```
4. Импортируйте данные
```
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

Добавьте API документацию:
1. Скопируйте папку docs на ваш сервер
```
scp -r имя_папки username@public_id:home/username
```
2. Найдите id контейнера nginx
```
docker container ls
```
3. Скопируйте данные из папки docs в контейнер nginx
```
docker cp docs/. <container_id>:/usr/share/nginx/html/api/docs
```

## Примеры:
Для просмотра документации с примерами перейдите по адресу:
http://51.250.111.79/api/docs/redoc.html
Панель администратора: http://51.250.111.79/admin
Главная страница сайта: http://51.250.111.79/recipes

