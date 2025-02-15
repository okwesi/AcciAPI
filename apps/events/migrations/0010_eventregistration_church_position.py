# Generated by Django 4.2.6 on 2024-12-20 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_remove_eventregistration_academy_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventregistration',
            name='church_position',
            field=models.CharField(blank=True, choices=[('elder', 'Elder'), ('pastor', 'Pastor'), ('deacon', 'Deacon'), ('member', 'Member'), ('deaconess', 'Deaconess'), ('prophet', 'Prophet'), ('prophetess', 'Prophetess'), ('apostle', 'Apostle'), ('reverend', 'Reverend'), ('other', 'Other'), ('none', 'None')], max_length=100, null=True),
        ),
    ]
