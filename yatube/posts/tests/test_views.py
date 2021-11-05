from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Albus')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='tesg',
        )
        post_list = [
            Post(
                author=cls.user,
                group=cls.group,
                image='posts/small.gif',
                text=f'Test {i}') for i in range(15)
        ]
        Post.objects.bulk_create(post_list)
        cls.first_post = Post.objects.first()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts:index': [
                'posts/index.html', None
            ],
            'posts:group_list': [
                'posts/group_list.html', {"slug": self.group.slug}
            ],
            'posts:profile': [
                'posts/profile.html', {"username": self.user}
            ],
            'posts:post_detail': [
                'posts/post_detail.html', {"post_id": self.first_post.pk}
            ],
            'posts:post_edit': [
                'posts/create_post.html', {"post_id": self.first_post.pk}
            ],
            'posts:post_create': [
                'posts/create_post.html', None
            ]
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name, template=template):
                response = self.authorized_client.get(
                    reverse(reverse_name, kwargs=template[1])
                )
                self.assertTemplateUsed(response, template[0])

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][0], self.first_post
        )

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)
        self.assertEqual(
            response.context['page_obj'][0], self.group.posts.first()
        )

    def test_none_group_and_side_group_correct_context(self):
        gr2 = Group.objects.create(
            title='Заголовок2',
            slug='te02'
        )
        Post.objects.bulk_create(
            [
                Post(
                    author=self.user,
                    group=gr2,
                    text='Test group assighnment'
                ),
                Post(
                    author=self.user,
                    text='Test group exempt'
                )
            ]
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': gr2.slug})
        )
        self.assertEqual(response.context['group'], gr2)
        self.assertEqual(response.context['page_obj'][0], gr2.posts.first())
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(
            response.context['count_posts'], self.user.posts.count()
        )
        self.assertEqual(
            response.context['page_obj'][0], self.user.posts.first()
        )

    def test_paginator_index_group_list_profile(self):
        reverse_name = {
            'posts:index': None,
            'posts:group_list': {"slug": self.group.slug},
            'posts:profile': {"username": self.user}
        }
        for name, params in reverse_name.items():
            with self.subTest(name=name, params=params):
                response = self.authorized_client.get(
                    reverse(name, kwargs=params)
                )
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.client.get(
                    reverse(name, kwargs=params) + '?page=2'
                )
                self.assertEqual(len(response.context['page_obj']), 5)
