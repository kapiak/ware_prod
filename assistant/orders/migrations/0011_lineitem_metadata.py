# Generated by Django 3.1 on 2020-08-25 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_auto_20200821_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
