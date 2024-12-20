# Generated by Django 5.1.2 on 2024-11-11 23:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('full_name', models.CharField(max_length=255)),
                ('category', models.CharField(choices=[('donation', 'Donation'), ('event', 'Event')], max_length=255)),
                ('category_object_id', models.PositiveIntegerField()),
                ('payment_method', models.CharField(max_length=255)),
                ('amount', models.PositiveIntegerField()),
                ('payment_started_at', models.DateTimeField()),
                ('payment_completed_at', models.DateTimeField()),
                ('reference_number', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=255)),
                ('currency', models.CharField(max_length=5)),
                ('receipt_number', models.CharField(blank=True, max_length=255, null=True)),
                ('gateway_response', models.CharField(blank=True, max_length=255, null=True)),
                ('authorization_code', models.CharField(blank=True, max_length=255, null=True)),
                ('fees', models.PositiveIntegerField(blank=True, null=True)),
                ('bank_name', models.CharField(blank=True, max_length=255, null=True)),
                ('customer_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('customer_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('transaction_object', models.JSONField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)ss', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_%(class)ss', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
            },
        ),
    ]
