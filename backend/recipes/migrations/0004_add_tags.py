import json

from django.db import migrations

JSON_FILE_PATH = '../data/tags.json'


def add_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')

    with open(JSON_FILE_PATH, encoding='utf-8') as file:
        tag_data = json.load(file)
        for tag in tag_data:
            new_tag = Tag(**tag)
            new_tag.save()


def remove_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    with open(JSON_FILE_PATH, encoding='utf-8') as file:
        tag_data = json.load(file)
        for tag in tag_data:
            Tag.objects.get(slug=tag['slug']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_add_ingredients'),
    ]

    operations = [
        migrations.RunPython(
            add_tags,
            remove_tags
        ),
    ]
