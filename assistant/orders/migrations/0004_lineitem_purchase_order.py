# Generated by Django 3.1 on 2020-08-19 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0003_remove_purchaseorderitem_sales_order_items'),
        ('orders', '0003_auto_20200813_0326'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='purchase_order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales_orders', to='purchases.purchaseorderitem'),
        ),
    ]
