from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            username='test-author',
            email='testauthor@mail.com',
            password='JimBeam1234')

        cls.post = Post.objects.create(
            text='текст ' * 10,
            author=cls.user
        )

    def test_post_str(self):
        text = ('текст ' * 10)[:15]
        post = PostModelTest.post
        to_str = post.__str__()
        self.assertEqual(to_str, text)

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст записи',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст записи',
            'group': 'Выберите группу для записи'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            description='текст ' * 10,
            slug='test-group',
        )

    def test_group_str(self):
        title = 'Название тестовой группы'
        to_str = GroupModelTest.group.__str__()
        self.assertEqual(to_str, title)

    def test_verbose_name(self):
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Введите название группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)
