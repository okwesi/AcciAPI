# Generated by Django 4.2.6 on 2024-12-20 21:51

import apps.shared.overrides
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_user_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=apps.shared.overrides.FileNameEngine('avatars/')),
        ),
    ]
