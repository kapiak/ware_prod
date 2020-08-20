# Generated by Django 3.1 on 2020-08-17 03:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('wagtailcore', '0052_pagelogentry'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('hero_tagline', models.CharField(blank=True, help_text='The tag line which appears on the top part of the hero image.', max_length=200, verbose_name='Hero Tagline')),
                ('hero_main_text', models.CharField(blank=True, help_text='The main text line which appears in the center part of the hero image.', max_length=200, verbose_name='Hero Main Text')),
                ('hero_subtext', models.CharField(blank=True, help_text='The subline text which appears under the main text of the hero image.', max_length=200, verbose_name='Hero Subtext')),
                ('hero_image', models.ForeignKey(help_text='The image which shows in the hero header of the page.', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]