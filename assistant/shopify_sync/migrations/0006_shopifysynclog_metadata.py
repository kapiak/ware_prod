# Generated by Django 3.1 on 2020-09-08 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_sync', '0005_auto_20200908_0945'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopifysynclog',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
