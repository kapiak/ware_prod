# Generated by Django 3.1 on 2020-08-19 05:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('weblink_channel', '0016_auto_20200819_0535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='sales_order_item',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_order_item', to='weblink_channel.weblinkorderitem'),
        ),
    ]