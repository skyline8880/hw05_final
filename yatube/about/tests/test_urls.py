from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_names_templates = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for adress, template in url_names_templates.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(reverse(adress))
                self.assertTemplateUsed(response, template)
