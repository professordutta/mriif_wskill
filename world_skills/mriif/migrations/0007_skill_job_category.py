# Generated by Django 5.1.4 on 2024-12-06 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mriif', '0006_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='job_category',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
