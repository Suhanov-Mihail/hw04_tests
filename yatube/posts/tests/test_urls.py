from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import Post, Group

from http import HTTPStatus

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='SnoopDog')
        Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
            description='Тестовое описание'
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        user = URLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(user)

    def test_not_authorized_url(self):
        """Страницы, доступные любому пользователю."""
        url_names = (
            '/',
            '/group/test-slug/',
            '/posts/1/',
            '/profile/SnoopDog/'
        )
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_author_only(self):
        """Страницы, доступные только автору."""
        response = self.authorized_client.get('/create/')
        response = self.authorized_client.get('/posts/1/edit')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/post_detail.html': '/posts/1/',
            'posts/profile.html': '/profile/SnoopDog/',
            'posts/create_post.html': '/posts/1/edit',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        """Запрос к несуществующей странице везвращает ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
