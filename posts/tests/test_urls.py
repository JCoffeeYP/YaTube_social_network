from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='IvanovII'),
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='IvanovII')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location(self):
        """Страница пользователя /<username>/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.post.author.username}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_post_id_url_exists_at_desired_location(self):
        """Страница поста пользователя /<username>/<post_id>/ доступна
        любому пользователю.
        """
        response = self.guest_client.get(
            reverse(
                'posts:post',
                kwargs={'username': PostURLTests.post.author.username,
                        'post_id': PostURLTests.post.id}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_post_id_url_is_available_for_author(self):
        """Страница редактирования поста /<username>/<post_id>/edit/ доступна автору.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'username': PostURLTests.post.author.username,
                        'post_id': PostURLTests.post.id}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_post_id_url_redirect_anonymous(self):
        """Страница редактирования поста /<username>/<post_id>/edit/
        недоступна незарегистрированному пользователю.
        """
        response = self.guest_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'username': PostURLTests.post.author.username,
                        'post_id': PostURLTests.post.id}
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_post_id_url_redirect_other_author(self):
        """Страница редактирования поста /<username>/<post_id>/edit/
        недоступна другому пользователю.
        """
        self.user_other = User.objects.create_user(username='SidorovAA')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_other)
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'username': PostURLTests.post.author.username,
                        'post_id': PostURLTests.post.id}
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_new_post_url_redirect_anonymous(self):
        """Страница /new/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(reverse('posts:new_post'))
        self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': './posts/index.html',
            '/group/test-slug/': 'group.html',
            '/new/': './posts/new_post.html',
            '/IvanovII/1/edit/': './posts/new_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_404pages_url(self):
        """Проверка возвращает ли сервер код 404, если страница не найдена."""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'Non_existent_user'}
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_cache_index_url(self):
        """Проверка cache на странице index."""
        response = self.authorized_client.get(reverse('posts:index'))
        previous_content = response.content
        Post.objects.create(
            text='Тестовый пост 1',
            author=self.user,
            )
        response = self.authorized_client.get(reverse('posts:index'))
        current_content = response.content
        self.assertEqual(previous_content, current_content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        last_content = response.content
        self.assertNotEquals(current_content, last_content)
