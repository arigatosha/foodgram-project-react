from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipes,
                            Tags)

User = get_user_model()


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра тегов."""

    class Meta:
        model = Tags
        fields = '__all__'
        read_only_fields = ('name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра ингридиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientWriteSerializer(serializers.Serializer):
    """Сериализатор записи ингридиентов в рецепт"""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Проверьте, что количество ингредиента больше 1!'
            )
        return value


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра ингридиентов в рецепте."""

    id = serializers.IntegerField(source='ingredient_id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'amount', 'measurement_unit')
        model = RecipeIngredient

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipesReadSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра рецепта."""

    tags = TagsSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            'tags',
            'author',
            'name',
            'image',
            'text',
            'id',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )
        read_only_fields = (
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_image(self, obj):
        return obj.image.url

    def get_ingredients(self, obj):
        return RecipeIngredientReadSerializer(
            obj.ingredients_amount.all(), many=True
        ).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipesWriteSerializer(serializers.ModelSerializer):
    """Сериализатор записи данных рецепта."""

    tags = TagsSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientWriteSerializer(many=True)
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'name', 'image', 'text',
                  'ingredients', 'cooking_time')

    def to_representation(self, instance):
        serializer = RecipesReadSerializer(instance, context=self.context)
        return serializer.data

    def add_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient,
                    pk=ingr.get('id')),
                amount=ingr.get('amount')
            ) for ingr in ingredients
        ])

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError('Необходим хотя бы 1 ингредиент')
        unique_ingredients = []
        for ingredient in ingredients:
            ingr_id = ingredient['id']
            if ingr_id not in unique_ingredients:
                unique_ingredients.append(ingr_id)
            else:
                raise ValidationError(
                    'Уберите дубль ингредиента'
                )
        return data

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < 1:
            raise ValidationError('Время приготовления должно быть больше 0')
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        cooking_time = validated_data.pop('cooking_time')
        author = serializers.CurrentUserDefault()(self)
        new_recipe = Recipes.objects.create(
            author=author,
            cooking_time=cooking_time,
            **validated_data
        )
        new_recipe.tags.set(tags)
        self.add_ingredients(new_recipe, ingredients)
        return new_recipe

    def update(self, recipe, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients_amount.all().delete()
            self.add_ingredients(recipe, ingredients)
        tags = self.initial_data.pop('tags')
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = Favorite
        fields = ('id',)


class RecipeListSerializer(serializers.ModelSerializer):
    '''
    Дополнительный сериализатор для отображения рецептов
    в подписках, избранном и покупках.
    '''

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепта в подписках."""

    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели подписок."""

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        return obj.user.follower.filter(author=obj.author).exists()

    def get_recipes(self, obj):
        queryset = obj.author.recipe.all()
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except ValueError:
                raise ValueError('Неверно задан параметр количества рецептов')
        return FollowRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipe.all().count()