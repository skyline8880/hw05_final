from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Albus')
        cls.us02 = User.objects.create_user(username='Severus')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='tesg',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.us02)

    def test_auth_user_url_correct_status(self):
        url_adress_status = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/profile/{self.user.username}/': 200,
            f'/posts/{self.post.pk}/': 200,
            f'/posts/{self.post.pk}/edit/': 200,
            '/create/': 200,
            '/unexisting_page/': 404,
        }
        for adress, status in url_adress_status.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, status)

    def test_guest_user_url_correct_status(self):
        url_adress_status = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/profile/{self.user.username}/': 200,
            f'/posts/{self.post.pk}/': 200,
            f'/posts/{self.post.pk}/edit/': 302,
            '/create/': 302,
            '/unexisting_page/': 404,
        }
        for adress, status in url_adress_status.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, status)

    def test_redirect_correct_adress(self):
        response = self.authorized_client2.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )
        self.assertRedirects(
            response, (f'/posts/{self.post.pk}/')
        )
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/')
        )

    def test_urls_uses_correct_template(self):
        url_names_templates = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in url_names_templates.items():
            with self.subTest(adress=adress, template=template):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_index_cache(self):
        response = self.authorized_client.get('/')
        self.assertContains(response, self.post, status_code=200)
        new_data = {
            'text': f'{self.post.text} 2'
        }
        self.authorized_client.post(
            '/create/',
            new_data,
        )
        response = self.authorized_client.get('/')
        self.assertNotContains(response, new_data.get('text'), status_code=200)
        cache.clear()
        response = self.authorized_client.get('/')
        self.assertContains(response, new_data.get('text'), status_code=200)
