import django_filters
from django_filters.rest_framework import FilterSet, filters
from django_filters import rest_framework

from recipes.models import Recipe, Tag, Ingredient


class IngredientFilter(rest_framework.FilterSet):
    """Фильтр для ингредиентов."""
    name = rest_framework.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр для рецептов: по избранному, списку покупок, автору и тегам."""
    name = django_filters.CharFilter(
        field_name='name',
    )
    author = django_filters.CharFilter(
        field_name='author',
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
