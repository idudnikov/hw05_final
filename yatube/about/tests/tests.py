from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls(self):
        """Проверка доступа страниц about"""
        url_names = ["/about/author/", "/about/tech/"]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_templates(self):
        """Проверка корректности использования шаблонов view-функциями"""
        templates_pages_names = {
            reverse("about:author"): "about/author.html",
            reverse("about:tech"): "about/tech.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
