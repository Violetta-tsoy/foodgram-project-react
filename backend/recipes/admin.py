from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingList, Tag


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    """Отображение данных модели Избранное"""
    list_display = ('user', 'recipe')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Отображение данных модели для списка покупок"""
    list_display = ('user', 'recipe')


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    """Отображение данных модели Тегов."""

    list_display = (
        'name',
        'color',
        'slug',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение данных модели Ингредиентов."""

    list_display = (
        'name',
        'measurement_unit',
    )

    search_fields = ('name',)


class IngredientsInline(admin.TabularInline):
    """
    Вспомогательный класс для возможности добавления ингредиентов
    в рецепт в панели администратоа.
    """

    model = Recipe.ingredients.through
    extra = 1


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    """Отображение данных модели Рецептов."""

    list_display = (
        'name',
        'author',
    )
    list_filter = (
        'name',
        'author',
        'tags',
    )

    readonly_fields = ('favorites_count',)

    inlines = (IngredientsInline,)

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        """
        Отображение количества раз, когда рецепт был добавлен кем-либо в список
        избранного.
        """
        return obj.favorites.count()
