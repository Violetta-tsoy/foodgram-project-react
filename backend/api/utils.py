from datetime import date

from rest_framework.generics import get_object_or_404

from recipes.models import Recipe


def serializer_add_method(serializer_name, request, recipe_id):
    user = request.user
    data = {'user': user.id, 'recipe': recipe_id}
    serializer = serializer_name(data=data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()


def serializer_delete_method(model, request, recipe_id):
    user = request.user
    get_object_or_404(
        model, user=user, recipe=get_object_or_404(Recipe, id=recipe_id)
    ).delete()


def export_ingredients(self, request, ingredients):
    user = self.request.user
    today = date.today()
    shopping_list = f'Список покупок пользователя: {user.username}\n\n'
    shopping_list += f"Дата: {today:%Y-%m-%d}\n\n"

    ingredient_lines = [
        f'- {ingredient["ingredient__name"]} '
        f'({ingredient["ingredient__measurement_unit"]}) - '
        f'{ingredient["amount"]}'
        for ingredient in ingredients
    ]
    shopping_list += "\n".join(ingredient_lines)
    shopping_list += f"\n\nFoodgram ({today:%Y})"
    return shopping_list
