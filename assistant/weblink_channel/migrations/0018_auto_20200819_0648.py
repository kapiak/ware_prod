# Generated by Django 3.1 on 2020-08-19 06:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20200813_0326'),
        ('weblink_channel', '0017_auto_20200819_0536'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorderitem',
            name='customer_order_item',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_order_item', to='orders.lineitem'),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('sent', 'Sent'), ('received', 'Received'), ('partial', 'Partially Recieved')], default='draft', max_length=100, verbose_name='Status'),
        ),
    ]
