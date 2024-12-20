# Generated by Django 5.1.2 on 2024-11-07 09:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_remove_event_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventamount',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_amounts', to='events.event'),
        ),
    ]
