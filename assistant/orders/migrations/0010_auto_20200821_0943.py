# Generated by Django 3.1 on 2020-08-21 09:43

from django.db import migrations
import wagtail.contrib.table_block.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_auto_20200821_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchorderupload',
            name='orders',
            field=wagtail.core.fields.StreamField([('upload', wagtail.contrib.table_block.blocks.TableBlock(table_options={'autoColumnSize': False, 'colHeaders': True, 'editor': 'text', 'height': 216, 'language': 'en', 'minSpareRows': 0, 'renderer': 'text', 'rowHeaders': False, 'startCols': 9, 'startRows': 1, 'stretchH': 'all'}))]),
        ),
    ]
