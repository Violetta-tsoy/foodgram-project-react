from datetime import date

from django.shortcuts import HttpResponse
from rest_framework import response, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import Recipe


def serializer_add_delete(serializer_name, model, request, recipe_id):
    user = request.user
    data = {'user': user.id, 'recipe': recipe_id}
    serializer = serializer_name(data=data, context={'request': request})
    if request.method == 'POST':
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED
        )
    get_object_or_404(
        model, user=user, recipe=get_object_or_404(Recipe, id=recipe_id)
    ).delete()
    return response.Response(status=status.HTTP_204_NO_CONTENT)


def ingredients_export(self, request, ingredients):
    user = self.request.user
    filename = f'{user.username}_shopping_list.txt'

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

    response = HttpResponse(
        shopping_list, content_type='text/plain; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def prohibited_method_response(request):
    message = 'Обращение к эндпоинту с данным методом не разрешено.'
    return Response(
        {'detail': message}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )
