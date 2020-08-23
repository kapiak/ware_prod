# Generated by Django 3.1 on 2020-08-23 02:57

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0010_auto_20200823_0249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='content',
            field=wagtail.core.fields.StreamField([('single_column', wagtail.core.blocks.StructBlock([('background_color', wagtail.core.blocks.ChoiceBlock(choices=[('bg-white', 'White'), ('bg-gray-900', 'Black'), ('bg-gray-500', 'Gray'), ('bg-red-500', 'Red'), ('bg-orange-500', 'Orange'), ('bg-yellow-500', 'Yellow'), ('bg-green-500', 'Green'), ('bg-teal-500', 'Teal'), ('bg-blue-500', 'Blue'), ('bg-indigo-500', 'Indigo'), ('bg-purple-500', 'Purple'), ('bg-pink-500', 'Pink')])), ('text_color', wagtail.core.blocks.ChoiceBlock(choices=[('text-white', 'White'), ('text-gray-900', 'Black'), ('text-gray-500', 'Gray'), ('text-red-500', 'Red'), ('text-orange-500', 'Orange'), ('text-yellow-500', 'Yellow'), ('text-green-500', 'Green'), ('text-teal-500', 'Teal'), ('text-blue-500', 'Blue'), ('text-indigo-500', 'Indigo'), ('text-purple-500', 'Purple'), ('bext-pink-500', 'Pink')])), ('column', wagtail.core.blocks.StreamBlock([('simple_card', wagtail.core.blocks.StructBlock([('background_color', wagtail.core.blocks.ChoiceBlock(choices=[('bg-white', 'White'), ('bg-gray-900', 'Black'), ('bg-gray-500', 'Gray'), ('bg-red-500', 'Red'), ('bg-orange-500', 'Orange'), ('bg-yellow-500', 'Yellow'), ('bg-green-500', 'Green'), ('bg-teal-500', 'Teal'), ('bg-blue-500', 'Blue'), ('bg-indigo-500', 'Indigo'), ('bg-purple-500', 'Purple'), ('bg-pink-500', 'Pink')])), ('text_color', wagtail.core.blocks.ChoiceBlock(choices=[('text-white', 'White'), ('text-gray-900', 'Black'), ('text-gray-500', 'Gray'), ('text-red-500', 'Red'), ('text-orange-500', 'Orange'), ('text-yellow-500', 'Yellow'), ('text-green-500', 'Green'), ('text-teal-500', 'Teal'), ('text-blue-500', 'Blue'), ('text-indigo-500', 'Indigo'), ('text-purple-500', 'Purple'), ('bext-pink-500', 'Pink')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('heading', wagtail.core.blocks.CharBlock(help_text='The title of the card which appears under the image.', max_length=255, min_length=10)), ('paragraph', wagtail.core.blocks.TextBlock(help_text='The paragraph text which appears in the card.', max_length=500, min_length=10))])), ('detail_card', wagtail.core.blocks.StructBlock([('background_color', wagtail.core.blocks.ChoiceBlock(choices=[('bg-white', 'White'), ('bg-gray-900', 'Black'), ('bg-gray-500', 'Gray'), ('bg-red-500', 'Red'), ('bg-orange-500', 'Orange'), ('bg-yellow-500', 'Yellow'), ('bg-green-500', 'Green'), ('bg-teal-500', 'Teal'), ('bg-blue-500', 'Blue'), ('bg-indigo-500', 'Indigo'), ('bg-purple-500', 'Purple'), ('bg-pink-500', 'Pink')])), ('text_color', wagtail.core.blocks.ChoiceBlock(choices=[('text-white', 'White'), ('text-gray-900', 'Black'), ('text-gray-500', 'Gray'), ('text-red-500', 'Red'), ('text-orange-500', 'Orange'), ('text-yellow-500', 'Yellow'), ('text-green-500', 'Green'), ('text-teal-500', 'Teal'), ('text-blue-500', 'Blue'), ('text-indigo-500', 'Indigo'), ('text-purple-500', 'Purple'), ('bext-pink-500', 'Pink')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('heading', wagtail.core.blocks.CharBlock(help_text='The title of the card which appears under the image.', max_length=255, min_length=10)), ('paragraph', wagtail.core.blocks.TextBlock(help_text='The paragraph text which appears in the card.', max_length=500, min_length=10))])), ('icon_bullets', wagtail.core.blocks.StructBlock([('icon', wagtail.core.blocks.CharBlock()), ('text', wagtail.core.blocks.CharBlock())])), ('rich_text', wagtail.core.blocks.RichTextBlock())], min_num=1))])), ('tow_columns', wagtail.core.blocks.StructBlock([('background_color', wagtail.core.blocks.ChoiceBlock(choices=[('bg-white', 'White'), ('bg-gray-900', 'Black'), ('bg-gray-500', 'Gray'), ('bg-red-500', 'Red'), ('bg-orange-500', 'Orange'), ('bg-yellow-500', 'Yellow'), ('bg-green-500', 'Green'), ('bg-teal-500', 'Teal'), ('bg-blue-500', 'Blue'), ('bg-indigo-500', 'Indigo'), ('bg-purple-500', 'Purple'), ('bg-pink-500', 'Pink')])), ('text_color', wagtail.core.blocks.ChoiceBlock(choices=[('text-white', 'White'), ('text-gray-900', 'Black'), ('text-gray-500', 'Gray'), ('text-red-500', 'Red'), ('text-orange-500', 'Orange'), ('text-yellow-500', 'Yellow'), ('text-green-500', 'Green'), ('text-teal-500', 'Teal'), ('text-blue-500', 'Blue'), ('text-indigo-500', 'Indigo'), ('text-purple-500', 'Purple'), ('bext-pink-500', 'Pink')])), ('left', wagtail.core.blocks.StreamBlock([('simple_card', wagtail.core.blocks.StructBlock([('background_color', wagtail.core.blocks.ChoiceBlock(choices=[('bg-white', 'White'), ('bg-gray-900', 'Black'), ('bg-gray-500', 'Gray'), ('bg-red-500', 'Red'), ('bg-orange-500', 'Orange'), ('bg-yellow-500', 'Yellow'), ('bg-green-500', 'Green'), ('bg-teal-500', 'Teal'), ('bg-blue-500', 'Blue'), ('bg-indigo-500', 'Indigo'), ('bg-purple-500', 'Purple'), ('bg-pink-500', 'Pink')])), ('text_color', wagtail.core.blocks.ChoiceBlock(choices=[('text-white', 'White'), ('text-gray-900', 'Black'), ('text-gray-500', 'Gray'), ('text-red-500', 'Red'), ('text-orange-500', 'Orange'), ('text-yellow-500', 'Yellow'), ('text-green-500', 'Green'), ('text-teal-500', 'Teal'), ('text-blue-500', 'Blue'), ('text-indigo-500', 'Indigo'), ('text-purple-500', 'Purple'), ('bext-pink-500', 'Pink')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('heading', wagtail.core.blocks.CharBlock(help_text='The title of the card which appears under the image.', max_length=255, min_length=10)), ('paragraph', wagtail.core.blocks.TextBlock(help_text='The paragraph text which appears in the card.', max_length=500, min_length=10))])), ('detail_card', wagtail.core.blocks.StructBlock([('background_color', wagtail.core.blocks.ChoiceBlock(choices=[('bg-white', 'White'), ('bg-gray-900', 'Black'), ('bg-gray-500', 'Gray'), ('bg-red-500', 'Red'), ('bg-orange-500', 'Orange'), ('bg-yellow-500', 'Yellow'), ('bg-green-500', 'Green'), ('bg-teal-500', 'Teal'), ('bg-blue-500', 'Blue'), ('bg-indigo-500', 'Indigo'), ('bg-purple-500', 'Purple'), ('bg-pink-500', 'Pink')])), ('text_color', wagtail.core.blocks.ChoiceBlock(choices=[('text-white', 'White'), ('text-gray-900', 'Black'), ('text-gray-500', 'Gray'), ('text-red-500', 'Red'), ('text-orange-500', 'Orange'), ('text-yellow-500', 'Yellow'), ('text-green-500', 'Green'), ('text-teal-500', 'Teal'), ('text-blue-500', 'Blue'), ('text-indigo-500', 'Indigo'), ('text-purple-500', 'Purple'), ('bext-pink-500', 'Pink')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('heading', wagtail.core.blocks.CharBlock(help_text='The title of the card which appears under the image.', max_length=255, min_length=10)), ('paragraph', wagtail.core.blocks.TextBlock(help_text='The paragraph text which appears in the card.', max_length=500, min_length=10))])), ('icon_bullets', wagtail.core.blocks.StructBlock([('icon', wagtail.core.blocks.CharBlock()), ('text', wagtail.core.blocks.CharBlock())])), ('rich_text', wagtail.core.blocks.RichTextBlock())], min_num=1)), ('right', wagtail.core.blocks.StreamBlock([('simple_card', wagtail.core.blocks.StructBlock([('background_color', wagtail.core.blocks.ChoiceBlock(choices=[('bg-white', 'White'), ('bg-gray-900', 'Black'), ('bg-gray-500', 'Gray'), ('bg-red-500', 'Red'), ('bg-orange-500', 'Orange'), ('bg-yellow-500', 'Yellow'), ('bg-green-500', 'Green'), ('bg-teal-500', 'Teal'), ('bg-blue-500', 'Blue'), ('bg-indigo-500', 'Indigo'), ('bg-purple-500', 'Purple'), ('bg-pink-500', 'Pink')])), ('text_color', wagtail.core.blocks.ChoiceBlock(choices=[('text-white', 'White'), ('text-gray-900', 'Black'), ('text-gray-500', 'Gray'), ('text-red-500', 'Red'), ('text-orange-500', 'Orange'), ('text-yellow-500', 'Yellow'), ('text-green-500', 'Green'), ('text-teal-500', 'Teal'), ('text-blue-500', 'Blue'), ('text-indigo-500', 'Indigo'), ('text-purple-500', 'Purple'), ('bext-pink-500', 'Pink')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('heading', wagtail.core.blocks.CharBlock(help_text='The title of the card which appears under the image.', max_length=255, min_length=10)), ('paragraph', wagtail.core.blocks.TextBlock(help_text='The paragraph text which appears in the card.', max_length=500, min_length=10))])), ('detail_card', wagtail.core.blocks.StructBlock([('background_color', wagtail.core.blocks.ChoiceBlock(choices=[('bg-white', 'White'), ('bg-gray-900', 'Black'), ('bg-gray-500', 'Gray'), ('bg-red-500', 'Red'), ('bg-orange-500', 'Orange'), ('bg-yellow-500', 'Yellow'), ('bg-green-500', 'Green'), ('bg-teal-500', 'Teal'), ('bg-blue-500', 'Blue'), ('bg-indigo-500', 'Indigo'), ('bg-purple-500', 'Purple'), ('bg-pink-500', 'Pink')])), ('text_color', wagtail.core.blocks.ChoiceBlock(choices=[('text-white', 'White'), ('text-gray-900', 'Black'), ('text-gray-500', 'Gray'), ('text-red-500', 'Red'), ('text-orange-500', 'Orange'), ('text-yellow-500', 'Yellow'), ('text-green-500', 'Green'), ('text-teal-500', 'Teal'), ('text-blue-500', 'Blue'), ('text-indigo-500', 'Indigo'), ('text-purple-500', 'Purple'), ('bext-pink-500', 'Pink')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('heading', wagtail.core.blocks.CharBlock(help_text='The title of the card which appears under the image.', max_length=255, min_length=10)), ('paragraph', wagtail.core.blocks.TextBlock(help_text='The paragraph text which appears in the card.', max_length=500, min_length=10))])), ('icon_bullets', wagtail.core.blocks.StructBlock([('icon', wagtail.core.blocks.CharBlock()), ('text', wagtail.core.blocks.CharBlock())])), ('rich_text', wagtail.core.blocks.RichTextBlock())], min_num=1))]))], blank=True),
        ),
    ]
