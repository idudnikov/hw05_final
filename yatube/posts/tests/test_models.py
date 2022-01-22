from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.post = Post.objects.create(
            author=cls.user,
            text="Test text",
        )

    def test_correct_object_name(self):
        """Проверка корректной работы __str__ у модели Post"""
        self.assertEqual(str(self.post), self.post.text)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Test group",
            slug="test_slug",
            description="Test description",
        )

    def test_correct_object_name(self):
        """Проверка корректной работы __str__ у модели Group"""
        self.assertEqual(str(self.group), self.group.title)
