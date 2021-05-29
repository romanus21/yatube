import tempfile

from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator
from django.test import Client, TestCase
from django.urls import reverse

from yatube import settings
from ..models import Post, User, Group, Follow


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create(
            username='test-author',
            email='testauthor@mail.com',
            password='JimBeam1234',
        )

        cls.user1 = User.objects.create(
            username='test-author-1',
            email='test2author@mail.com',
            password='JimBeam1234',
        )

        cls.user2 = User.objects.create(
            username='test-author-2',
            email='test2author@mail.com',
            password='JimBeam1234',
        )

        Follow.objects.create(user=cls.user, author=cls.user1)

        cls.group1 = Group.objects.create(
            title='Название тестовой группы 1',
            description='текст ' * 10,
            slug='test-group-1',
        )

        cls.group2 = Group.objects.create(
            title='Название тестовой группы 2',
            description='текст ' * 10,
            slug='test-group-2',
        )

        cls.post = Post.objects.create(
            text='текст ' * 10,
            author=cls.user,
            group=cls.group1,
        )

        Post.objects.create(
            text='текст ' * 10,
            author=cls.user,
            group=cls.group2,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.user)
        self.templates_url_names = {
            'base.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'test-group-1'}),
            'new_post.html': reverse('new_post'),
        }

    def test_pages_uses_correct_template(self):
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_correct_context_index(self):
        response = self.authorized_client.get(reverse('index'))
        user = PostsPagesTests.user

        post_text_0 = response.context.get('paginator').object_list[0].text
        post_author_0 = response.context.get('paginator').object_list[0].author

        self.assertEqual(post_text_0, 'текст ' * 10)
        self.assertEqual(post_author_0, user)

    def test_correct_context_group(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-group-1'}))
        user = PostsPagesTests.user

        post_text_0 = response.context.get('paginator').object_list[0].text
        post_author_0 = response.context.get('paginator').object_list[0].author
        group_title = response.context.get('group').title

        self.assertEqual(post_text_0, 'текст ' * 10)
        self.assertEqual(post_author_0, user)
        self.assertEqual(group_title, 'Название тестовой группы 1')

    def test_correct_context_new_post(self):
        response = self.authorized_client.get(reverse('new_post'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_correct_context_edit_post(self):
        user = PostsPagesTests.user
        response = self.authorized_client.get(reverse('edit_post', kwargs={
            'username': user.username,
            'post_id': 1}))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_correct_context_profile(self):
        user = PostsPagesTests.user
        response = self.authorized_client.get(reverse('profile', kwargs={
            'username': user.username}))

        profile = response.context.get('profile')
        self.assertEqual(profile, PostsPagesTests.user)

        count_posts = response.context.get('count_posts')
        self.assertEqual(count_posts, 2)

        posts = profile.posts.all()
        paginator = Paginator(posts, 10).object_list

        page_response = response.context.get('page').object_list
        paginator_response = response.context.get('paginator').object_list

        for post in page_response:
            self.assertIn(post, posts)
        for post in paginator_response:
            self.assertIn(post, paginator)

    def test_correct_context_post(self):
        user = PostsPagesTests.user
        response = self.authorized_client.get(reverse('post', kwargs={
            'username': user.username,
            'post_id': PostsPagesTests.post.id}))

        post = PostsPagesTests.post
        post_response = response.context.get('post')
        self.assertEqual(post, post_response)

        profile = response.context.get('profile')
        self.assertEqual(user, profile)

    def test_paginator_index(self):
        response = self.authorized_client.get(reverse('index'))

        posts = len(response.context.get('paginator').object_list)
        self.assertGreater(10, posts)

    def test_cache(self):
        before_response = self.authorized_client.get(reverse('index'))

        Post.objects.create(
            text='текст ' * 10,
            author=PostsPagesTests.user,
        )
        after_response = self.authorized_client.get(reverse('index'))
        self.assertEqual(before_response.content, after_response.content)

        cache.clear()
        after_response = self.authorized_client.get(reverse('index'))
        self.assertNotEqual(before_response.content, after_response.content)

    def test_follow(self):
        self.authorized_client.get((reverse('profile_follow', kwargs={
            'username': PostsPagesTests.user2.username})))
        self.assertTrue(Follow.objects.filter(user=PostsPagesTests.user,
                                              author=PostsPagesTests.user2)
                        .exists())

    def test_unfollow(self):
        self.authorized_client.get((reverse('profile_unfollow', kwargs={
            'username': PostsPagesTests.user1.username})))

        self.assertFalse(Follow.objects.filter(
            user=PostsPagesTests.user,
            author=PostsPagesTests.user1).exists())

    def test_unauthorized_comment(self):
        response = self.guest_client.get(reverse('add_comment', kwargs={
            'username': PostsPagesTests.user.username,
            'post_id': PostsPagesTests.post.id,
        }))
        self.assertEqual(response.status_code, 302)

    def test_image_index(self):
        small_pic = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_pic,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст 2',
            'group': PostsPagesTests.group1.id,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        urls = {
            reverse('index'),
            reverse('group', kwargs={
                'slug': PostsPagesTests.group1.slug
            }),
            reverse('profile', kwargs={
                'username': PostsPagesTests.user.username
            }),
        }

        for url in urls:
            response = self.authorized_client.get(url)
            post = response.context['page'][0]
            self.assertTrue(post.image)

        response = self.authorized_client.get(reverse('post', kwargs={
            'username': PostsPagesTests.user.username,
            'post_id': PostsPagesTests.user.posts.latest().pk
        }))

        post = response.context['post']
        self.assertTrue(post.image)
