# Generated by Django 3.0.9 on 2020-08-11 09:13

import assistant.orders.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_measurement.models
import measurement.measures.mass
import modelcluster.fields
import uuid
import wagtail.search.index


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0003_auto_20200810_1252'),
        ('addresses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('number', models.CharField(help_text="The order 's position in the shop's count of orders starting at 1001. Order numbers are sequential and start at 1001.", max_length=255, unique=True, verbose_name='Order Number')),
                ('user_email', models.EmailField(blank=True, default='', max_length=254)),
                ('customer_id', models.CharField(blank=True, max_length=255, null=True)),
                ('total_price', models.DecimalField(decimal_places=2, help_text='The sum of all line item prices, discounts, shipping, taxes, and tips in the shop currency. Must be positive.', max_digits=10)),
                ('subtotal_price', models.DecimalField(decimal_places=2, help_text='The price of the order in the shop currency after discounts but before shipping, taxes, and tips.', max_digits=10, null=True)),
                ('total_tax', models.DecimalField(decimal_places=2, help_text='The sum of all the taxes applied to the order in th shop currency. Must be positive.', max_digits=10, null=True)),
                ('weight', django_measurement.models.MeasurementField(default=assistant.orders.models.zero_weight, measurement=measurement.measures.mass.Mass)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('unfulfilled', 'Unfulfilled'), ('partially fulfilled', 'Partially Fulfilled'), ('fulfilled', 'Fulfilled'), ('canceled', 'Canceled')], default='unfulfilled', max_length=32)),
                ('type', models.CharField(choices=[('regular', 'Orders by customers'), ('draft', 'Created by staff, Not confirmed')], default='regular', max_length=32)),
                ('cancel_reason', models.CharField(blank=True, choices=[('customer', 'Customer'), ('fraud', 'Fraud'), ('inventory', 'Inventory'), ('declined', 'Declined'), ('other', 'Other')], help_text='The reason why the order was canceled.', max_length=100, verbose_name='Cancel Reason')),
                ('cancelled_at', models.DateTimeField(blank=True, help_text='The date and time when the order was canceled.', null=True, verbose_name='Canceled at')),
                ('closed_at', models.DateTimeField(blank=True, help_text='The date and time when the order was closed.', null=True, verbose_name='Closed at')),
                ('billing_address', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='addresses.Address')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_orders_order', to=settings.AUTH_USER_MODEL)),
                ('shipping_address', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='addresses.Address')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_orders_order', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('is_shipping_required', models.BooleanField()),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('quantity_fulfilled', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_orders_lineitem', to=settings.AUTH_USER_MODEL)),
                ('order', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='orders.Order')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_orders_lineitem', to=settings.AUTH_USER_MODEL)),
                ('variant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_lines', to='products.ProductVariant')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
    ]
