# Generated by Django 3.1 on 2020-09-10 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_sync', '0007_eventstore'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventstore',
            name='error_data',
            field=models.JSONField(blank=True, default=dict, verbose_name='Error Data'),
        ),
        migrations.AddField(
            model_name='eventstore',
            name='status',
            field=models.CharField(choices=[('received', 'Received'), ('in-process', 'In Process'), ('success', 'Success'), ('failed', 'Failed')], default='received', max_length=50, verbose_name='Status'),
        ),
    ]