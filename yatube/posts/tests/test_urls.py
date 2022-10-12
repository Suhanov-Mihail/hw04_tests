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
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_only(self):
        """Страницы, доступные только автору."""
        response = self.authorized_client.get('/create/')
        response2 = self.authorized_client.get('/posts/1/edit/')
        response3 = self.guest_client.get('/create/')
        response4 = self.guest_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response2.status_code, HTTPStatus.OK)
        self.assertEqual(response3.status_code, HTTPStatus.FOUND)
        self.assertEqual(response4.status_code, HTTPStatus.FOUND)

    def test_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/posts/1/': 'posts/post_detail.html',
            '/profile/SnoopDog/': 'posts/profile.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        """Запрос к несуществующей странице везвращает ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
