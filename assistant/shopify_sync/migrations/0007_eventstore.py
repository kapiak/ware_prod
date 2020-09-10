# Generated by Django 3.1 on 2020-09-10 04:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shopify_sync', '0006_shopifysynclog_metadata'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventStore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('domain', models.CharField(blank=True, max_length=100, verbose_name='Domain')),
                ('topic', models.CharField(blank=True, max_length=100, verbose_name='Topic')),
                ('data', models.JSONField(blank=True, default=dict)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_shopify_sync_eventstore', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_shopify_sync_eventstore', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Event Store',
                'verbose_name_plural': 'Events Store',
            },
        ),
    ]
