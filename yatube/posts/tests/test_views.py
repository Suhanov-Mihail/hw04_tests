from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from .. models import Post, Group

TEST_OF_POST: int = 13
TEN_POST: int = 10
THREE_POST: int = 3
User = get_user_model()


class VIEWSTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='SnoopDog2')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.group_wihtout_posts = Group.objects.create(
            title='Тестовый заголовок группы без постов',
            slug='no_slug',
            description='Тестовое описание группы без постов'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись для создания нового поста',
            group=cls.group,)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='SnoopDog3')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group_list',
                     kwargs={'slug': 'test-slug'})): 'posts/group_list.html',
            (reverse('posts:profile',
                     kwargs={'username': 'SnoopDog2'})): 'posts/profile.html',
            (reverse('posts:post_detail',
                     kwargs={
                         'post_id': self.post.pk})): 'posts/post_detail.html',
            (reverse('posts:post_edit',
                     kwargs={
                         'post_id': self.post.pk})): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Тест контекста для index.html."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post)

    def test_group_posts_correct_context(self):
        """Тест контекста для group_posts."""
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug':
                                                      self.group.slug}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post)

    def test_profile_correct_context(self):
        """Тест контекста для profile."""
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username':
                                                      self.post.author.username
                                                      }))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post)

    def test_post_detail_correct_context(self):
        """Тест контекста для post_detail."""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id':
                                                      self.post.id}))
        first_object = response.context['posts']
        self.assertEqual(first_object, self.post)
        self.assertEqual(first_object.author.posts.count(),
                         self.post.author.posts.count())

    def test_create_correct_context(self):
        """Тест контекста для post_create."""
        response = self.authorized_client.get(reverse(
            'posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_correct_context(self):
        """Тест контекста для edit."""
        response = self.authorized_author.get(reverse('posts:post_edit',
                                              kwargs={'post_id':
                                                      self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Здесь без .fields.get(value) у меня всё ломается
                # и тест не работает. сам я не допер как эт сделать,
                # в слаке тоже ничего особо не подсказали.
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(form_field, expected)

    def test_create_post_home_group_list_profile_pages(self):
        """Созданный пост отобразился на главной,
        на странице группы и в профиле пользователя.
        """
        list_urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            ),
        )
        for tested_url in list_urls:
            response = self.authorized_author.get(tested_url)
            self.assertEqual(len(response.context['page_obj'].object_list), 1)

    def test_no_post_in_another_group_posts(self):
        """Пост не попал в группу,
        для которой не был предназначен.
        """
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group_wihtout_posts.slug}))
        posts = response.context['page_obj']
        self.assertEqual(0, len(posts))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='SnoopDog4')
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='slug_test',
            description='Тестовое описание')
        cls.posts = []
        for i in range(TEST_OF_POST):
            cls.posts.append(Post(
                text=f'Тестовый пост {i+1}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def test_paginator(self):
        """Тест паджинатора"""
        list_urls = {
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.author}),
        }
        for tested_url in list_urls:
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context.get('page_obj'
                                                      ).object_list),
                                                     TEN_POST)

        for tested_url in list_urls:
            response = self.client.get(tested_url, {'page': 2})
            self.assertEqual(len(response.context.get('page_obj'
                                                      ).object_list),
                                                     THREE_POST)
