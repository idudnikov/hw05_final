import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Test group",
            slug="Test_slug",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Test post",
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_correct_templates(self):
        """Проверка корректности использования шаблонов view-функциями"""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": self.post.author}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post.pk}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post.pk}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_correct_context(self):
        """Проверка корректности контекста на главной странице"""
        first_object = self.author_client.get(reverse("posts:index")).context[
            "page_obj"
        ][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_group_list_page_correct_context(self):
        """Проверка корректности контекста на странице с постами группы"""
        context = self.author_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        ).context
        first_object = context["page_obj"][0]
        self.assertEqual(context["group"], self.group)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_profile_page_correct_context(self):
        """Проверка корректности контекста на странице профиля"""
        context = self.author_client.get(
            reverse("posts:profile", kwargs={"username": self.post.author})
        ).context
        first_object = context["page_obj"][0]
        self.assertEqual(context["author"], self.post.author)
        self.assertEqual(
            context["posts_count"],
            Post.objects.filter(author=self.user).count(),
        )
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_post_detail_page_correct_context(self):
        """Проверка корректности контекста на странице поста"""
        context = self.author_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk})
        ).context
        self.assertEqual(context["post"], self.post)
        self.assertEqual(
            context["user_posts_count"],
            Post.objects.filter(author=self.post.author).count(),
        )

    def test_edit_post_page_correct_form(self):
        """Проверка корректности формы на странице редактирования поста"""
        context = self.author_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk})
        ).context
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        self.assertEqual(context["post_id"], self.post.pk)
        self.assertEqual(context["groups"].get(), Group.objects.get())
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_page_correct_form(self):
        """Проверка корректности формы на странице создания поста"""
        context = self.author_client.get(reverse("posts:post_create")).context
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        self.assertEqual(context["groups"].get(), Group.objects.get())
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_with_group_correct_mapping_index_page(self):
        """Проверка корректного отображения на сайте поста с выбранной
        группой на главной странице"""
        group = Group.objects.create(title="Group 0", slug="group_0")
        post_with_group = Post.objects.create(
            author=self.user, text="Test post with group", group=group
        )
        response = self.author_client.get(reverse("posts:index"))
        self.assertEqual(response.context["page_obj"][0], post_with_group)

    def test_post_with_group_correct_mapping_group_list_page(self):
        """Проверка корректного отображения на сайте поста с выбранной
        группой на странице с постами группы"""
        group = Group.objects.create(title="Group 0", slug="group_0")
        post_with_group = Post.objects.create(
            author=self.user, text="Test post with group", group=group
        )
        response = self.author_client.get(
            reverse("posts:group_list", kwargs={"slug": group.slug})
        )
        self.assertEqual(response.context["page_obj"][0], post_with_group)

    def test_post_with_group_correct_mapping_profile_page(self):
        """Проверка корректного отображения на сайте поста с выбранной
        группой на странице профиля пользователя"""
        group = Group.objects.create(title="Group 0", slug="group_0")
        post_with_group = Post.objects.create(
            author=self.user, text="Test post with group", group=group
        )
        response = self.author_client.get(
            reverse(
                "posts:profile", kwargs={"username": post_with_group.author}
            )
        )
        self.assertEqual(response.context["page_obj"][0], post_with_group)

    def test_post_with_group_correct_mapping_other_group_list_page(self):
        """Проверка того, что пост с выбранной группой не отображается на
        странице с постами другой группы"""
        group = Group.objects.create(title="Group 0", slug="group_0")
        post_with_group = Post.objects.create(
            author=self.user, text="Test post with group", group=group
        )
        response = self.author_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        self.assertNotEqual(response.context["page_obj"][0], post_with_group)


class PostViewPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Test group",
            slug="Test_slug",
        )
        objs = (
            Post(author=cls.user, text="Test post", group=cls.group)
            for _ in range(15)
        )
        Post.objects.bulk_create(objs)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_paginator_index_page_contains_ten_records(self):
        """Проверка паджинатора на главной странице"""
        response = self.author_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_paginator_index_page_contains_five_records(self):
        """Проверка паджинатора на главной странице"""
        response = self.author_client.get(reverse("posts:index") + "?page=2")
        self.assertEqual(len(response.context["page_obj"]), 5)

    def test_paginator_group_list_page_contains_ten_records(self):
        """Проверка паджинатора на странице с постами группы"""
        response = self.author_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_paginator_group_list_page_contains_five_records(self):
        """Проверка паджинатора на странице с постами группы"""
        response = self.author_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 5)

    def test_paginator_profile_page_contains_ten_records(self):
        """Проверка паджинатора на странице профиля"""
        response = self.author_client.get(
            reverse("posts:profile", kwargs={"username": self.user})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_paginator_profile_page_contains_five_records(self):
        """Проверка паджинатора на странице профиля"""
        response = self.author_client.get(
            reverse("posts:profile", kwargs={"username": self.user})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 5)


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="author")
        cls.user = User.objects.create_user(username="user")
        cls.following_user = User.objects.create_user(username="follower")

    def setUp(self):
        self.user_client = Client()
        self.user_client.force_login(self.user)
        self.following_user_client = Client()
        self.following_user_client.force_login(self.following_user)

    def test_user_can_follow_and_unfollow(self):
        """Проверка того, что авторизованный пользователь может подписываться и
        отписываться от автора"""
        self.user_client.get(
            reverse("posts:profile_follow", kwargs={"username": self.author})
        )
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )
        self.user_client.get(
            reverse("posts:profile_unfollow", kwargs={"username": self.author})
        )
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )

    def test_new_post_correct_mapping(self):
        """Проверка того, что новый пост появляется у тех, кто подписан на
        автора и не появляется у тех, кто не подписан на автора"""
        Follow.objects.create(author=self.author, user=self.following_user)
        post = Post.objects.create(author=self.author, text="Test post")
        response = self.following_user_client.get(
            reverse("posts:follow_index")
        )
        self.assertTrue(post in response.context["page_obj"])
        response = self.user_client.get(reverse("posts:follow_index"))
        self.assertFalse(post in response.context["page_obj"])
