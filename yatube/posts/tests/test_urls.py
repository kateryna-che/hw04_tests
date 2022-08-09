from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-post',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(
            User.objects.create_user(username='client')
        )

    def test_page_for_everyone(self):
        url_names = (
            '/',
            '/group/test-slug/',
            '/profile/auth/',
            f'/posts/{self.post.pk}/',
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting-page/')
        self.assertEqual(response.status_code, 404)

    def test_authorized_author(self):
        response = self.authorized_author.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_authorized_client(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_redirect_client(self):
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.pk}/')

    def test_redirect_unauthorized(self):
        urls = {
            f'/posts/{self.post.pk}/edit/':
                f'/auth/login/?next=/posts/{self.post.pk}/edit/',
            '/create/': '/auth/login/?next=/create/',
        }
        for url, redirect in urls.items():
            with self.subTest(url=url):
                self.assertRedirects(self.guest_client.get(url), redirect)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',

        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)
