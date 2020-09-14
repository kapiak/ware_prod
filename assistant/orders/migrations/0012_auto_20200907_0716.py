# Generated by Django 3.1 on 2020-09-07 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_lineitem_metadata'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('unfulfilled', 'Unfulfilled'), ('partially_fulfilled', 'Partially Fulfilled'), ('fulfilled', 'Fulfilled'), ('canceled', 'Canceled')], default='unfulfilled', max_length=32),
        ),
    ]