import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Albus')
        cls.group = Group.objects.create(
            title='Тест-группа',
            slug='tesg'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )
        cls.posts_count = Post.objects.count()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        form_data = {
            'text': 'Новая запись',
            'group': self.post.group.pk,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            text=form_data.get('text'),
            group=form_data.get('group'),
            author=self.user
        ).exists())
        self.assertEqual(Post.objects.count(), self.posts_count + 1)

    def test_edit_post(self):
        form_data = {
            'text': 'Новая запись2',
            'group': self.post.group.pk,
        }
        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': Post.objects.first().pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            text=form_data.get('text'),
            group=form_data.get('group'),
            author=self.user
        ).exists())
        self.post.refresh_from_db()
        self.assertEqual(Post.objects.count(), self.posts_count)

    def test_create_task(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Запись с картинкой',
            'group': self.post.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertTrue(
            Post.objects.filter(
                text=form_data.get('text'),
                group=form_data.get('group'),
                image=f'posts/{uploaded.name}'
            ).exists()
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)

    def able_to_comment_post(self):
        form_data = {
            'text': 'Коммент'
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': Post.objects.first().pk}
            )
        )
        self.assertTrue(
            Comment.objects.filter(text=form_data.get('text')).exists()
        )
        self.assertContains(response, form_data.get('text'), status_code=200)
