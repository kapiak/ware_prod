# Generated by Django 3.1 on 2020-08-19 03:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20200813_0326'),
        ('weblink_channel', '0013_auto_20200818_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='weblinkorder',
            name='order',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='weblink_order', to='orders.order'),
        ),
    ]