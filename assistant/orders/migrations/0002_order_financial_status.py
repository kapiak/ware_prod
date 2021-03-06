# Generated by Django 3.0.9 on 2020-08-13 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='financial_status',
            field=models.CharField(choices=[('authorized', 'Authorized'), ('pending', 'Pending'), ('paid', 'Paid'), ('partially_paid', 'Partially Paid'), ('refunded', 'Refunded'), ('voided', 'Voided'), ('partially_refunded', 'Partially Refunded'), ('any', 'Any'), ('unpaid', 'Unpaid')], default='unpaid', max_length=100, verbose_name='Financial Status'),
        ),
    ]
