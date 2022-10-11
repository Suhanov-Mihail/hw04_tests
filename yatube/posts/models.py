from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

POST_LEN = 15


class Group(models.Model):
    """Модель для хранения групп"""
    title = models.CharField(max_length=200,
                             verbose_name='name')
    slug = models.SlugField(unique=True,
                            verbose_name='addres')
    description = models.TextField(verbose_name='description')

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель для хранения постов"""
    text = models.TextField(verbose_name='text')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='date')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='author',
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='group',
        related_name='posts'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:POST_LEN]