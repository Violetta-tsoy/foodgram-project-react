import base64

from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.db.transaction import atomic
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import exceptions, relations, serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingList,
    Tag,
)
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, image_string = data.split(';base64,')
            file_extension = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(image_string),
                name=f'temp.{file_extension}'
            )
        return super().to_internal_value(data)

# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')
#             ext = format.split('/')[-1]
#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

#         return super().to_internal_value(data)

class UserGetSerializer(UserSerializer):
    """Сериализатор для просмотра профиля пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False

        return Follow.objects.filter(
            author=obj, user=request.user
        ).exists()


class UserRecipesSerializer(UserGetSerializer):
    """Сериализатор для просмотра пользователя с рецептами."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = UserGetSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, object):
        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipe_limit')
        queryset = object.recipes.all()
        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]

        return RecipeShortSerializer(queryset, context=context, many=True).data


class UserPostSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения краткой информации о рецептах."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(UserGetSerializer):
    """Сериализатор для подписок."""
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Follow
        fields = ('author', 'user', )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['author', 'user', ],
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def create(self, validated_data):
        return Follow.objects.create(
            user=self.context.get('request').user, **validated_data)

    def validate_author(self, value):
        if self.context.get('request').user == value:
            raise serializers.ValidationError({
                'errors': 'Подписка на самого себя не возможна!'
            })
        return value


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецептах."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class FavoriteAndShoppingCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления рецептов в список избранного и корзину.
    """
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    class Meta:
        abstract = True
        fields = ('user', 'recipe')


class FavoriteSerializer(FavoriteAndShoppingCreateSerializer):
    """Сериализатор для добавления рецептов в избранное."""

    class Meta(FavoriteAndShoppingCreateSerializer.Meta):
        model = Favorite
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['recipe', 'user', ],
                message='Этот рецепт уже добавлен в избранное.'
            )
        ]

    def create(self, validated_data):
        return self.Meta.model.objects.create(
            user=self.context.get('request').user, **validated_data
        )


class ShoppingListSerializer(FavoriteAndShoppingCreateSerializer):
    """Сериализатор для создания списка покупок."""

    class Meta(FavoriteAndShoppingCreateSerializer.Meta):
        model = ShoppingList
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=['recipe', 'user', ],
                message='Этот рецепт уже добавлен в список покупок.'
            )
        ]

    def create(self, validated_data):
        return self.Meta.model.objects.create(
            user=self.context.get('request').user, **validated_data
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Определение логики сериализации для чтения (отображения) объектов модели
    рецептов.
    """

    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    is_favorited = serializers.BooleanField(default=False, read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        default=False, read_only=True
    )
    ingredients = IngredientRecipeSerializer(
        many=True, read_only=True, source='ingredient_list'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализотор для создания рецептов."""

    tags = relations.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'tags',
            'author',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    @atomic
    def create_bulk_ingredients(self, ingredients, recipe):
        ingredients_list = []
        for ingredient in ingredients:
            current_ingredient = ingredient['ingredient']['id']
            current_amount = ingredient.get('amount')
            ingredients_list.append(
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=current_ingredient,
                    amount=current_amount
                )
            )
        IngredientRecipe.objects.bulk_create(ingredients_list)

    @atomic
    def create(self, validated_data):
        try:
            ingredients_list = validated_data.pop('ingredients')
            tags = validated_data.pop('tags')
            author = self.context.get('request').user
            recipe = Recipe.objects.create(author=author, **validated_data)
            recipe.save()
            recipe.tags.set(tags)
            self.create_bulk_ingredients(ingredients_list, recipe)
            return recipe
        except IntegrityError:
            error_message = (
                'Название рецепта с данным именем у Вас уже существует!'
            )
            raise serializers.ValidationError({'error': error_message})

    @atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_bulk_ingredients(recipe=instance, ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not len(ingredients) != 0:
            raise exceptions.ValidationError(
                {'ingredients': 'Невозможно добавить рецепт без ингредиентов!'}
            )
        ingredients_list = []
        for item in ingredients:
            if item['id'] in ingredients_list:
                raise exceptions.ValidationError(
                    {'ingredients': 'Ингредиенты не могут повторяться!'}
                )
            ingredients_list.append(item['id'])
            if int(item['amount']) < 1:
                raise exceptions.ValidationError(
                    {
                        'amount': (
                            'Количество ингредиентов не может быть меньше 1'
                        )
                    }
                )
        return data

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                {'cooking_time': (
                    'Время приготовления рецепта не может меньше и равным 0!'
                )}
            )
        return data

    def validate_tags(self, data):
        tags = self.initial_data.get('tags', False)
        if not tags:
            raise exceptions.ValidationError(
                {'tags': 'Рецепт не может быть создан без тегов!'}
            )
        tags_list = []
        for tags in tags:
            if tags in tags_list:
                raise exceptions.ValidationError(
                    {'tags': 'Нельзя использовать повторяющиеся теги!'}
                )
            tags_list.append(tags)
        return data
