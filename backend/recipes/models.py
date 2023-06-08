from django.contrib.auth import get_user_model
from django.core import validators
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    """Модель Тегов."""

    name = models.CharField(
        max_length=200,
        verbose_name='Тег'
    )
    color = models.CharField(
        unique=True,
        max_length=7,
        help_text='Введите цвет в RGB-формате (#rrggbb)',
        validators=[
            validators.RegexValidator(
                r'^#[a-fA-F0-9]{6}$',
                'Используйте RGB-формат для указания цвета (#AABBCC)',
            )
        ],
    )
    slug = models.SlugField(
        verbose_name='Название slug',
        help_text='Введите название slug',
        unique=True,
        max_length=200,
    )

    class Meta:
        ordering = ('id',)
        verbose_name_plural = 'Теги'
        default_related_name = 'tags'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Модель ингредиентов"""

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения ингредиента.',
        max_length=200,
    )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'

    class Meta:
        ordering = ('-id',)
        verbose_name_plural = 'Ингредиенты'
        indexes = [
            models.Index(fields=['name'], name='name_index'),
        ]


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        max_length=200,
        help_text='Введите название рецепта'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Введите дату публикации рецепта',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        help_text='Введите автора рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    text = models.TextField(
        verbose_name='Описание приготовления блюда',
        help_text='Введите описание приготовления блюда',
    )
    tags = models.ManyToManyField(Tag, related_name='tags')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='ingredients',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Введите время приготовления блюда в минутах',
        validators=[
            MinValueValidator(
                1,
                message='Укажите время больше либо равное 1'
            ),
        ],
    )

    def __str__(self) -> str:
        return f'id: {self.id} Автор: {str(self.author)} Название: {self.name}'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
        )


class IngredientRecipe(models.Model):
    """Модель для связи рецепта и соответствующих ему ингредиентов."""

    name = models.CharField(
        'Название',
        max_length=200,
        help_text='Введите название',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_list',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_list',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Введите количество ингредиентов',
        validators=[
            MinValueValidator(
                1,
                message='Укажите количество больше либо равное 1'
            ),
        ],
    )

    def __str__(self):
        return f'{self.ingredient} {self.amount}'

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe',
            )
        ]


class FavoritesAndShopping(models.Model):
    """
    Модель для формирования наследуемых моделей Favorite и
    ShoppingList.
    """

    user = models.ForeignKey(
        User, verbose_name='Пользователь', on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favorite(FavoritesAndShopping):
    """Избранные рецепты."""

    class Meta(FavoritesAndShopping.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class ShoppingList(FavoritesAndShopping):
    """Рецепты, добавленные в список покупок."""

    class Meta(FavoritesAndShopping.Meta):
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        default_related_name = 'shopping_list'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
