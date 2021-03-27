import os
import shutil

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'temp_media'))
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        testimage_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small_3.gif',
            content=testimage_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='IvanovII'),
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.get(username='IvanovII')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            './posts/index.html': reverse('posts:index'),
            'group.html': (
                reverse('posts:group_posts', kwargs={'slug': 'test-slug'})
            ),
            './posts/new_post.html': reverse('posts:new_post')
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page'][0]
        author = first_post.author
        text = first_post.text
        pub_date = first_post.pub_date
        group = first_post.group
        self.assertEqual(author, PostPagesTests.post.author)
        self.assertEqual(text, PostPagesTests.post.text)
        self.assertEqual(pub_date, PostPagesTests.post.pub_date)
        self.assertEqual(group, PostPagesTests.post.group)
        self.assertTrue(PostPagesTests.post.image)

    def test_group_page_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'})
        )
        first_post = response.context['page'][0]
        author = first_post.author
        text = first_post.text
        pub_date = first_post.pub_date
        group = first_post.group
        self.assertEqual(author, PostPagesTests.post.author)
        self.assertEqual(text, PostPagesTests.post.text)
        self.assertEqual(pub_date, PostPagesTests.post.pub_date)
        self.assertEqual(group, PostPagesTests.post.group)
        self.assertTrue(PostPagesTests.post.image)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон new_post при редактировании сформирован
        с правильным контекстом
        """
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'username': self.user.username,
                                       'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        first_post = response.context['page'][0]
        author_post = response.context['author'].username
        text = first_post.text
        pub_date = first_post.pub_date
        post_count = response.context['post_count']
        self.assertEqual(author_post, self.user.username)
        self.assertEqual(text, PostPagesTests.post.text)
        self.assertEqual(pub_date, PostPagesTests.post.pub_date)
        self.assertEqual(post_count, 1)
        self.assertTrue(PostPagesTests.post.image)

    def test_profile_post_id_page_show_correct_context(self):
        """Шаблон отдельного поста сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post', kwargs={'username': self.user.username,
                                  'post_id': self.post.id}))
        unique_post = response.context['post'].id
        author_post = response.context['author'].username
        post_count = response.context['post_count']
        self.assertEqual(unique_post, self.post.id)
        self.assertEqual(author_post, self.user.username)
        self.assertEqual(post_count, 1)

    def test_check_new_post_on_index_page(self):
        """Проверка наличия поста на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page']), 1)

    def test_check_new_post_on_group_page(self):
        """Проверка наличия поста на странице группы"""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page']), 1)

    def test_check_new_post_not_in_wrong_group(self):
        """Проверка отсутствия поста на странице другой группы"""
        self.wrong_group = Group.objects.create(
            title='Лишняя группа',
            slug='wrong-group',
            description='Тестовое описание лишней группы'
        )
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'wrong-group'})
        )
        check_post = response.context['page']
        self.assertFalse(check_post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='IvanovII')
        for i in range(13):
            Post.objects.create(
                text=f'{i} Тестовый пост',
                author=User.objects.get(username='IvanovII'),
            )

    def setUp(self):
        self.user = User.objects.get(username='IvanovII')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_containse_ten_records(self):
        '''Паджинатор на 1-й странице index выдаёт верное количество записей'''
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        '''Паджинатор на 2-й странице index выдаёт верное количество записей'''
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
