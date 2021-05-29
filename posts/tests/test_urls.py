from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, User, Post


class PostsUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Название тестовой группы',
            description='текст ' * 10,
            slug='test-slug',
        )

        cls.user1 = User.objects.create(
            username='Test-User-1',
            email='testauthor1@mail.com',
            password='JimBeam1234',
        )

        cls.user2 = User.objects.create(
            username='Test-User-2',
            email='testauthor2@mail.com',
            password='JimBeam1234',
        )

        cls.post = Post.objects.create(
            text='текст ' * 10,
            author=cls.user1,
            group=cls.group,
        )

        cls.templates_url_names = {
            'base.html': reverse('index'),
            'group.html': reverse('group',
                                  kwargs={'slug': PostsUrlTest.group.slug}),
            'new_post.html': reverse('new_post'),
            'profile.html': reverse('profile', kwargs={
                'username': PostsUrlTest.user1.username}),
            'post.html': reverse('post', kwargs={
                'username': PostsUrlTest.user1.username,
                'post_id': PostsUrlTest.post.id}),
        }

        cls.edit_post_url = reverse('edit_post', kwargs={
            'username': PostsUrlTest.user1.username,
            'post_id': PostsUrlTest.post.id})

        cls.post_url = reverse('post', kwargs={
            'username': PostsUrlTest.user1.username,
            'post_id': PostsUrlTest.post.id})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsUrlTest.user1)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(PostsUrlTest.user2)

    def test_urls_uses_correct_template(self):
        for template, reverse_name in PostsUrlTest.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_correct_access(self):
        for reverse_name in PostsUrlTest.templates_url_names.values():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, 200)

    def test_unauthorized_new_post_access(self):
        response = self.guest_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 302)

    def test_correct_edit_access(self):
        url = PostsUrlTest.edit_post_url

        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, 302,
                         'Неавторизованный клиент не перенаправляется')

        response = self.another_authorized_client.get(url)
        self.assertEqual(response.status_code, 302,
                         'Авторизованный не-автор поста не перенаправляется')

        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_correct_template_edit(self):
        url = PostsUrlTest.edit_post_url

        response = self.authorized_client.get(url)
        self.assertTemplateUsed(response, 'edit_post.html')

    def test_correct_redirect_edit(self):
        url = PostsUrlTest.edit_post_url

        response = self.another_authorized_client.get(url)
        self.assertRedirects(response, PostsUrlTest.post_url, 302, 200,
                             ('Авторизованный не-автор ' +
                              'поста перенаправляется не туда'))


class StaticPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        site = Site.objects.get(pk=1)

        cls.flatpages = [
            reverse('about-author'),
            reverse('about-spec'),
        ]

        for url in cls.flatpages:
            FlatPage.objects.create(
                url=url,
                title=url.replace('/', ''),
                content='<b>content</b>'
            ).sites.add(site)

    def setUp(self):
        self.guest_client = Client()

    def test_flatpages_access(self):
        for url in StaticPagesTest.flatpages:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)
