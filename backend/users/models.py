from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    username = models.CharField(
        null=False,
        blank=False,
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
    )
    email = models.EmailField(
        null=False,
        blank=False,
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    password = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'username',
                    'email',
                ],
                name='unique_user',
            )
        ]

        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок на других пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписан на автора',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_user_author'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')), name='no_self_follow'
            ),
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
