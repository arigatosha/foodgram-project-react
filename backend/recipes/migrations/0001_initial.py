# Generated by Django 3.2.19 on 2023-06-14 13:23

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re
import recipes.validators
import users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранное',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название ингредиента', max_length=150, validators=[users.validators.UserNameValidator()], verbose_name='Название инградиента')),
                ('measurement_unit', models.CharField(help_text='Введите единицы измерения', max_length=16, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=1, help_text='Введите количество инградиента в рецепте', validators=[django.core.validators.MinValueValidator(1, message='Минимальное количество - 1')], verbose_name='Количество инградиентов')),
            ],
            options={
                'verbose_name': 'Ингредиент в рецепте',
                'verbose_name_plural': 'Ингредиенты в рецепте',
            },
        ),
        migrations.CreateModel(
            name='Recipes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название рецепта', max_length=200, unique=True, validators=[users.validators.UserNameValidator()], verbose_name='Название рецепта')),
                ('image', models.ImageField(help_text='Добавьте файл с изображением', upload_to='recipes/image/', verbose_name='Изображение блюда')),
                ('text', models.TextField(verbose_name='Описание рецепта')),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
                ('cooking_time', models.PositiveSmallIntegerField(default=1, help_text='Время приготовления в минутах', validators=[django.core.validators.MinValueValidator(1, message='Время приготовления не может быть меньше 1 минуты!')], verbose_name='Время приготовления в минутах')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название тега', max_length=200, unique=True, validators=[users.validators.UserNameValidator()], verbose_name='Название тега')),
                ('color', models.CharField(help_text='Введите цвет тега в виде HEX-кода', max_length=7, unique=True, validators=[recipes.validators.ColorValidator], verbose_name='Цвет в HEX')),
                ('slug', models.SlugField(help_text='Введите короткое название тега', max_length=200, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid')], verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(help_text='Рецепт в списке покупок', on_delete=django.db.models.deletion.CASCADE, related_name='+', to='recipes.recipes', verbose_name='Рецепт в списке покупок')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
            },
        ),
    ]