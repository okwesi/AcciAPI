# Generated by Django 5.1.2 on 2024-11-12 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pledge',
            name='is_redeemed',
            field=models.BooleanField(default=False),
        ),
    ]
