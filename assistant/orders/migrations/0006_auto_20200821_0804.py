# Generated by Django 3.1 on 2020-08-21 08:04

from django.db import migrations
import wagtail.contrib.table_block.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_batchorderupload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchorderupload',
            name='orders',
            field=wagtail.core.fields.StreamField([('upload', wagtail.contrib.table_block.blocks.TableBlock(table_options={'autoColumnSize': False, 'colHeaders': False, 'editor': 'text', 'height': 216, 'language': 'en', 'minSpareRows': 0, 'renderer': 'text', 'rowHeaders': True, 'startCols': 4, 'startRows': 6, 'stretchH': 'all'}))]),
        ),
    ]
