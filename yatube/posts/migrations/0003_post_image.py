# Generated by Django 2.2.16 on 2022-01-17 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0002_auto_20220117_1544"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="image",
            field=models.ImageField(
                blank=True, upload_to="posts/", verbose_name="Картинка"
            ),
        ),
    ]