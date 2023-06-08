import json

from django.db import migrations

JSON_FILE_PATH = '../data/ingredients.json'


def add_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')

    with open(JSON_FILE_PATH, encoding='utf-8') as file:
        ingredient_data = json.load(file)
        for ingredient in ingredient_data:
            new_ingredient = Ingredient(**ingredient)
            new_ingredient.save()


def remove_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')

    with open(JSON_FILE_PATH, encoding='utf-8') as file:
        ingredient_data = json.load(file)
        for ingredient in ingredient_data:
            Ingredient.objects.get(name=ingredient['name']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_ingredients,
            remove_ingredients
        ),
    ]
