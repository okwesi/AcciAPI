# Generated by Django 4.2.6 on 2024-08-31 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jurisdiction', '0004_alter_branch_options_alter_branch_address_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='branch',
            name='area',
        ),
    ]
