from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
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

    def test_text_label(self):
        """verbose_name поля text совпадает с ожидаемым."""
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEquals(verbose, 'Текст записи')

    def test_text_help_text(self):
        """help_text поля text совпадает с ожидаемым."""
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        self.assertEquals(help_text, 'Чем бы вы хотели поделиться с миром?')

    def test_object_name_is_post_field(self):
        """__str__  post - это строчка с содержимым post.text."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEquals(expected_object_name, str(post))

    def test_object_name_is_group_field(self):
        """__str__  group - это строчка с содержимым group.title."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))
