# Generated by Django 3.1 on 2020-08-19 09:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import uuid
import wagtail.search.index


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0003_auto_20200813_0326'),
        ('products', '0004_auto_20200813_0203'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('number', models.CharField(max_length=100, verbose_name='Number')),
                ('estimated_arrival', models.IntegerField(verbose_name='Estimated Arrival in Days')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('received', 'Received'), ('partial', 'Partially Received')], default='draft', max_length=100, verbose_name='Status')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_purchases_purchaseorder', to=settings.AUTH_USER_MODEL)),
                ('sales_order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchase_orders', to='orders.order')),
                ('supplier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_orders', to='products.supplier')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_purchases_purchaseorder', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Purchase Order',
                'verbose_name_plural': 'Purchase Orders',
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
        migrations.CreateModel(
            name='PurchaseOrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('quantity', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('received', 'Received'), ('partial', 'Partially Received')], default='draft', max_length=100, verbose_name='Status')),
                ('received', models.PositiveIntegerField(default=0)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_purchases_purchaseorderitem', to=settings.AUTH_USER_MODEL)),
                ('purchase_order', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='purchases.purchaseorder')),
                ('sales_order_item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_order_item', to='orders.lineitem')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_purchases_purchaseorderitem', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Purchase Order Item',
                'verbose_name_plural': 'Purchase Order Items',
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
    ]