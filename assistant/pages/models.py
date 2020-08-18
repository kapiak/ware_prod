from django.db import models
from django.utils.translation import gettext_lazy as _


from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class HomePage(Page):
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        related_name="+",
        on_delete=models.PROTECT,
        help_text=_("The image which shows in the hero header of the page."),
    )
    hero_tagline = models.CharField(
        verbose_name=_("Hero Tagline"),
        max_length=200,
        blank=True,
        help_text=_(
            "The tag line which appears on the top part of the hero image."
        ),
    )
    hero_main_text = models.CharField(
        verbose_name=_("Hero Main Text"),
        max_length=200,
        blank=True,
        help_text=_(
            "The main text line which appears in the center part of the hero image."
        ),
    )
    hero_subtext = models.CharField(
        verbose_name=_("Hero Subtext"),
        max_length=200,
        blank=True,
        help_text=_(
            "The subline text which appears under the main text of the hero image."
        ),
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel("hero_image"),
        FieldPanel('hero_tagline'),
        FieldPanel('hero_main_text'),
        FieldPanel('hero_subtext'),
    ]

    def _str__(self):
        return f"{self.title}"
