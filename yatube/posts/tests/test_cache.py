from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post

User = get_user_model()


class PostCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.post = Post.objects.create(
            author=cls.user,
            text="Test post",
        )
        objs = (Post(author=cls.user, text="Test post") for _ in range(3))
        Post.objects.bulk_create(objs)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_new_post_not_in_cache(self):
        """Проверка того, что удаленный пост остается в кэше"""
        new_post = Post.objects.create(author=self.user, text="New post")
        first_response = self.author_client.get(reverse("posts:index"))
        self.assertEqual(first_response.context["page_obj"][0], new_post)
        Post.objects.filter(pk=new_post.id).delete()
        second_response = self.author_client.get(reverse("posts:index"))
        self.assertEqual(first_response.content, second_response.content)
        cache.clear()
        third_response = self.author_client.get(reverse("posts:index"))
        self.assertNotEqual(new_post, third_response.context["page_obj"][0])
