import json

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient

JSON_FILE_PATH = 'D:\\Dev\\foodgram-project-react/data/ingredients.json'


class Command(BaseCommand):
    help = 'Импорт данных из файла JSON в таблицу Ingredients.'

    def handle(self, *args, **kwargs):
        if Ingredient.objects.exists():
            raise CommandError('Очистите базу перед загрузкой JSON файла.')

        try:
            with open(JSON_FILE_PATH, encoding='utf-8') as file:
                ingredient_data = json.load(file)
                ingredients = [
                    Ingredient(**ingredient) for ingredient in ingredient_data
                ]
                Ingredient.objects.bulk_create(
                    ingredients, ignore_conflicts=True
                )

        except json.JSONDecodeError as e:
            raise CommandError(
                f'Ошибка выполнения команды importjson.'
                f'Ошибка разбора JSON: {str(e)}'
            ) from e

        self.stdout.write(
            self.style.SUCCESS(f'Фаил {file.name} успешно импортирован.')
        )
