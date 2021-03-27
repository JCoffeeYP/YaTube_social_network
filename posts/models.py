from textwrap import shorten

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст записи',
        help_text='Чем бы вы хотели поделиться с миром?'
    )
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Название группы',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Изображение',
        help_text='Если есть что показать, выкладывай!'
        )

    def __str__(self) -> str:
        return shorten(self.text, width=15)

    class Meta:
        ordering = ('-pub_date',)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Добавьте комментарий'
    )
    created = models.DateTimeField('date published', auto_now_add=True),
