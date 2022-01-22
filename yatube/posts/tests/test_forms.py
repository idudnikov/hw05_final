from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Test group",
            slug="Test_slug",
        )
        cls.post = Post.objects.create(
            author=cls.user, text="Test post", group=cls.group
        )
        cls.group_1 = Group.objects.create(
            title="Test group 1",
            slug="Test_slug_1",
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.post.author)

    def test_new_text_post_created_in_db(self):
        """Проверка сохранения в БД нового текстового поста"""
        form_data = {"text": "Test post text only"}
        posts_count = Post.objects.count()
        self.author_client.post(reverse("posts:post_create"), data=form_data)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user, text=form_data["text"]
            ).exists()
        )

    def test_new_post_with_group_created_in_db(self):
        """Проверка сохранения в БД нового поста с группой"""
        form_data = {"text": "Test post with group", "group": self.group.id}
        posts_count = Post.objects.count()
        self.author_client.post(reverse("posts:post_create"), data=form_data)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=form_data["text"],
                group=form_data["group"],
            ).exists()
        )

    def test_new_post_with_image_created_in_db(self):
        """Проверка сохранения в БД нового поста с картинкой"""
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
        form_data = {"text": "Test post with image", "image": uploaded}
        posts_count = Post.objects.count()
        self.author_client.post(reverse("posts:post_create"), data=form_data)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user, text=form_data["text"]
            ).exists()
        )

    def test_edited_post_changes(self):
        """Проверка сохранения внесенных в редактируемый пост изменений
        в БД"""
        form_data = {"text": "Test text 2", "group": self.group_1.id}
        self.author_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=form_data,
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, "Test text 2")
        self.assertEqual(self.post.group, self.group_1)

    def test_created_comment_correct_mapping(self):
        """Проверка сохранения комментария в БД"""
        form_data = {"text": "Test comment"}
        self.author_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.pk}),
            data=form_data,
        )
        response = self.author_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk})
        )
        comment = response.context["comments"][0]
        self.assertEqual(comment.text, form_data["text"])
        self.assertEqual(comment.post, self.post)
