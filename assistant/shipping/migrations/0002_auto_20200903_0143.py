# Generated by Django 3.1 on 2020-09-03 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingmethod',
            name='meta',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
