# Generated by Django 5.1.4 on 2025-05-03 12:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mriif', '0015_enquiry_how_did_you_hear'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EnquiryNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('enquiry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enquiry_notes', to='mriif.enquiry')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
