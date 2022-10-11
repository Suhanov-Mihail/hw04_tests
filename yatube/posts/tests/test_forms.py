from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.forms import PostForm

from http import HTTPStatus

User = get_user_model()


class PostCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='DogSnoops')
        cls.group = Group.objects.create(
            title='Тестовый титул',
            slug='test_slag',
            description='Тестовое описание'
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_post(self):
        """При создании валидной формы создается запись в бд"""
        count = Post.objects.count()
        form_data = {
            'text': 'Сообщение',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(text='Сообщение')
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': 'DogSnoops'}))
        self.assertEqual(post.text, form_data['text'])

    def test_guest_new_post(self):
        """Гостевой пользователь не может создавать посты"""
        form_data = {
            'text': 'Пост от гостевого пользователя',
            'group': self.group.id
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Пост от гостевого пользователя').exists())

    def test_authorized_edit_post(self):
        """Авторизованный пользователь может редактировать пост"""
        form_data = {
            'text': 'Сообщение2',
            'group': self.group.id
        }
        self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_two = Post.objects.get(text='Сообщение2')
        self.client.get(f'/posts/{post_two.id}/edit')
        form_data = {
            'text': 'Измененное сообщение',
            'group': self.group.id
        }
        response_edit = self.author_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post_two.id
                    }),
            data=form_data,
            follow=True,
        )
        post_two = Post.objects.get(text='Измененное сообщение')
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
        self.assertEqual(post_two.text, form_data['text'])
