# Generated by Django 5.1.2 on 2024-11-02 17:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_rename_comment_count_post_comments_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userinteraction',
            unique_together=set(),
        ),
    ]
