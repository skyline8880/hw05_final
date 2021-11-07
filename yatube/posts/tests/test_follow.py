from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, Follow

User = get_user_model()


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Albus')
        cls.us02 = User.objects.create_user(username='Severus')
        cls.us03 = User.objects.create_user(username='Rubeus')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='tesg',
        )
        post_list = [
            Post(
                author=cls.user,
                group=cls.group,
                text=f'Test {i}') for i in range(5)
        ]
        Post.objects.bulk_create(post_list)
        cls.first_post = Post.objects.first()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.us02)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(self.us03)

    def test_follow_author(self):
        self.authorized_client2.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.us02,
                author=self.user
            ).exists()
        )

    def test_unfollow_author(self):
        Follow.objects.create(user=self.us02, author=self.user)
        self.authorized_client2.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.user})
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.us02,
                author=self.user
            ).exists()
        )

    def test_post_list_user_following_author(self):
        Follow.objects.create(user=self.us02, author=self.user)
        post_list2 = [
            Post(
                author=self.us03,
                group=self.group,
                text=f'Test_follow {i}') for i in range(2)
        ]
        Post.objects.bulk_create(post_list2)
        response = self.authorized_client2.get(reverse('posts:follow_index'))
        self.assertEqual(
            response.context['page_obj'][0], self.user.posts.first()
        )
        response = self.authorized_client2.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][0], self.us03.posts.first()
        )
        response = self.authorized_client3.get(reverse('posts:follow_index'))
        self.assertNotContains(response, self.user.posts.first())
        response = self.authorized_client3.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][0], self.us03.posts.first()
        )
