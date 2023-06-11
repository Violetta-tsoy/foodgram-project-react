# FOODGFAM
<!-- ![Deploy badge](https://github.com/Violetta-tsoy/foodgram-project-react/actions/workflows/foodgram-project-react_workflow.yml/badge.svg)  -->
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
Команда для заполнения базы данными:
```
docker-compose exec backend python manage.py loaddata ingredients.json
```

## Примеры:
Для просмотра документации с примерами перейдите по адресу: http://localhost/api/docs/