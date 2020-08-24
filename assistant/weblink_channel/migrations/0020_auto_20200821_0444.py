# Generated by Django 3.1 on 2020-08-21 04:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('weblink_channel', '0019_auto_20200819_0907'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='customer_order_item',
        ),
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='purchase_order',
        ),
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='sales_order_item',
        ),
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='weblinkorder',
            name='address',
        ),
        migrations.RemoveField(
            model_name='weblinkorder',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='weblinkorder',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='weblinkorder',
            name='order',
        ),
        migrations.RemoveField(
            model_name='weblinkorder',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='weblinkorderitem',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='weblinkorderitem',
            name='order',
        ),
        migrations.RemoveField(
            model_name='weblinkorderitem',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='weblinkorderitem',
            name='variant',
        ),
        migrations.DeleteModel(
            name='PurchaseOrder',
        ),
        migrations.DeleteModel(
            name='PurchaseOrderItem',
        ),
        migrations.DeleteModel(
            name='WebLinkOrder',
        ),
        migrations.DeleteModel(
            name='WebLinkOrderItem',
        ),
    ]