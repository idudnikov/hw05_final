from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="author")
        cls.not_author = User.objects.create_user(username="not_author")
        cls.group = Group.objects.create(
            title="Test group",
            slug="Test_slug",
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="Test group",
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.not_author)

    def test_unexisting_page_access(self):
        """Проверка доступа к несуществующей странице и кастомного шаблона"""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")

    def test_unauthorized_user_access(self):
        """Проверка доступа неавторизованного клиента к страницам сайта"""
        url_names = [
            "/",
            f"/group/{self.group.slug}/",
            f"/profile/{self.author}/",
            f"/posts/{self.post.pk}/",
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_user_creates_post(self):
        """Проверка доступа неавторизованного клиента к странице создания
        поста и правильного редиректа на страницу аутентификации"""
        response = self.guest_client.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, "/auth/login/?next=/create/")

    def test_authorized_user_creates_post(self):
        """Проверка доступа авторизованного клиента к странице создания
        поста"""
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_edits_post(self):
        """Проверка доступа автора поста к странице редактирования поста"""
        response = self.author_client.get(f"/posts/{self.post.pk}/edit/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_templates(self):
        """Проверка использования корректных шаблонов"""
        templates_url_names = {
            "/": "posts/index.html",
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/profile/{self.post.author}/": "posts/profile.html",
            f"/posts/{self.post.pk}/": "posts/post_detail.html",
            "/create/": "posts/create_post.html",
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_author_edits_post_correct_template(self):
        """Проверка использования корректного шаблона при запросе автора на
        изменение поста"""
        response = self.author_client.get(f"/posts/{self.post.pk}/edit/")
        self.assertTemplateUsed(response, "posts/create_post.html")

    def test_unauthorized_user_cannot_comment(self):
        """Проверка того, что неавторизованный пользователь не может оставлять
        комментарии"""
        response = self.guest_client.get(f"/posts/{self.post.pk}/comment/")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, f"/auth/login/?next=/posts/{self.post.pk}/comment/"
        )
