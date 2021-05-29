import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostCreateForm
from ..models import Post, User, Group


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create(
            username='test-author',
            email='testauthor@mail.com',
            password='JimBeam1234',
        )

        cls.post = Post.objects.create(
            text='текст' * 10,
            author=cls.user,
        )

        cls.group = Group.objects.create(
            title='Название тестовой группы',
            description='текст ' * 10,
            slug='test-slug',
        )

        cls.form = PostCreateForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Task."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, reverse('index'))

        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(Post.objects.
                        filter(text=form_data['text'],
                               author=PostCreateFormTests.user).exists())

    def test_edit_post_text(self):
        post_id = PostCreateFormTests.post.id
        old_text = PostCreateFormTests.post.text
        user = PostCreateFormTests.user

        self.authorized_client.post(
            reverse('edit_post', kwargs={
                'username': user.username,
                'post_id': post_id}
                    ),
            data={
                'text': 'Тестовый текст',
            },
            follow=True,
        )

        new_post = PostCreateFormTests.post
        new_post.refresh_from_db()

        self.assertNotEqual(old_text, new_post.text)

    def test_edit_post_group(self):
        post_id = PostCreateFormTests.post.id
        old_group = PostCreateFormTests.post.group
        user = PostCreateFormTests.user
        group = PostCreateFormTests.group

        self.authorized_client.post(
            reverse('edit_post', kwargs={
                'username': user.username,
                'post_id': post_id}
                    ),
            data={
                'text': PostCreateFormTests.post.text,
                'group': group.id
            },
            follow=True,
        )

        new_post = PostCreateFormTests.post
        new_post.refresh_from_db()

        self.assertNotEqual(old_group, new_post.group)
