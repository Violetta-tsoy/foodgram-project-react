# Generated by Django 3.2 on 2023-06-07 05:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(help_text='Введите время приготовления блюда в минутах', validators=[django.core.validators.MinValueValidator(1, message='Укажите время больше либо равное 1')], verbose_name='Время приготовления (в минутах)'),
        ),
    ]
