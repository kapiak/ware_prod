# Generated by Django 3.1 on 2020-08-18 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('weblink_channel', '0006_auto_20200818_0641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='sales_order_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puchase_order_item', to='weblink_channel.weblinkorderitem', unique=True),
        ),
    ]
