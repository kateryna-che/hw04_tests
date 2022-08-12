from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description',
        )
        cls.group_without_posts = Group.objects.create(
            title='test-group-without-posts',
            slug='test-slug-without-posts',
            description='test-description-without-posts',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-post',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def post_attributes_test(self, page, kwargs=None):
        response = self.authorized_client.get(reverse(
            page, kwargs=kwargs)
        )
        post = response.context['page_obj'][0]
        post_attributes = {
            post.text: self.post.text,
            post.author: self.post.author,
            post.group: self.post.group,
        }
        for test_attribute, attribute in post_attributes.items():
            self.assertEqual(test_attribute, attribute)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_index_show_correct_context(self):
        self.post_attributes_test('posts:index')

    def test_post_group_list_show_correct_context(self):
        self.post_attributes_test('posts:group_list', {'slug': self.post.group.slug})

    def test_post_profile_show_correct_context(self):
        self.post_attributes_test('posts:profile', {'username': self.post.author})

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context['post'].id, self.post.id)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id})
        )
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_create_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_creating_post(self):
        self.assertNotEqual(self.post.group, self.group_without_posts)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_paginator = User.objects.create_user(
            username='user-paginator'
        )
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description',
        )
        Post.objects.bulk_create([
            Post(
                author=cls.user_paginator,
                text='test-post',
                group=cls.group
            )
            for i in range(13)
        ])

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user_paginator)

    def test_paginator(self):
        pages = {
            'posts:index': '',
            'posts:group_list': {'slug': self.group.slug},
            'posts:profile': {'username': self.user_paginator},
        }
        for page, kwargs in pages.items():
            with self.subTest(page=page):
                pages_num = {'1': 10, '2': 3}
                for num, posts in pages_num.items():
                    response = self.client.get(
                        reverse(page, kwargs=kwargs) + f'?page={num}'
                    )
                    self.assertEqual(len(response.context['page_obj']), posts)
