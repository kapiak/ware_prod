# Generated by Django 3.1 on 2020-08-18 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weblink_channel', '0008_auto_20200818_0657'),
    ]

    operations = [
        migrations.AddField(
            model_name='weblinkorder',
            name='status',
            field=models.CharField(choices=[('new', 'New'), ('init', 'Puchase Order Made'), ('submitted', 'Submitted Purchase Order'), ('stock-recieved', 'Stock Recieved'), ('sent', 'Stock Sent to Customer'), ('cancelled', 'Order Cancelled')], default='new', max_length=100, verbose_name='Status'),
        ),
    ]