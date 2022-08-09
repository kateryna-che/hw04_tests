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
        cls.group2 = Group.objects.create(
            title='test-group2',
            slug='test-slug2',
            description='test-description2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-post',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.post.group.slug})
        )
        self.assertEqual(response.context['group'], self.post.group)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post.author})
        )
        self.assertEqual(response.context['author'], self.post.author)

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
        self.assertNotEqual(self.post.group, self.group2)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description',
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)
        self.user_paginator = User.objects.create_user(
            username='user-paginator'
        )
        for i in range(13):
            Post.objects.create(
                author=self.user_paginator,
                text='test-post',
                group=self.group,
            )
        Post.objects.create(
            author=self.user,
            text='test-post',
        )

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_four_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': 'user-paginator'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        response = self.client.get(
            reverse('posts:profile',
                    kwargs={'username': 'user-paginator'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
