# Generated by Django 5.1.2 on 2024-11-17 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donation', '0007_donationpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pledge',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
    ]
