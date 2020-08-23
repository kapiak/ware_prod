from django.db import models
from django.forms import formset_factory
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel

from assistant.weblink_channel.forms import (
    CustomerInformationForm,
    ProductAddForm,
    ShippingInformationForm,
)


class ColorChoices(models.TextChoices):
    """Color choices from tailwindcss"""

    WHITE = "bg-white", _("White")
    BLACK = "bg-gray-900", _("Black")
    GRAY = "bg-gray-500", _("Gray")
    RED = "bg-red-500", _("Red")
    ORANGE = "bg-orange-500", _("Orange")
    YELLOW = "bg-yellow-500", _("Yellow")
    GREEN = "bg-green-500", _("Green")
    TEAL = "bg-teal-500", _("Teal")
    BLUE = "bg-blue-500", _("Blue")
    INDIGO = "bg-indigo-500", _("Indigo")
    PURPLE = "bg-purple-500", _("Purple")
    PINK = "bg-pink-500", _("Pink")


class TextColorChoices(models.TextChoices):
    """Color choices from tailwindcss"""

    WHITE = "text-white", _("White")
    BLACK = "text-gray-900", _("Black")
    GRAY = "text-gray-500", _("Gray")
    RED = "text-red-500", _("Red")
    ORANGE = "text-orange-500", _("Orange")
    YELLOW = "text-yellow-500", _("Yellow")
    GREEN = "text-green-500", _("Green")
    TEAL = "text-teal-500", _("Teal")
    BLUE = "text-blue-500", _("Blue")
    INDIGO = "text-indigo-500", _("Indigo")
    PURPLE = "text-purple-500", _("Purple")
    PINK = "bext-pink-500", _("Pink")


class CardWithImageBlockBase(blocks.StructBlock):
    """Base Struct Block for a card with an image"""

    background_color = blocks.ChoiceBlock(choices=ColorChoices.choices)
    text_color = blocks.ChoiceBlock(choices=TextColorChoices.choices)
    image = ImageChooserBlock()
    heading = blocks.CharBlock(
        max_length=255,
        min_length=10,
        help_text=_("The title of the card which appears under the image."),
    )
    paragraph = blocks.TextBlock(
        max_length=500,
        min_length=10,
        help_text=_("The paragraph text which appears in the card."),
    )


class CardDetailBlock(CardWithImageBlockBase):
    class Meta:
        icon = "user"
        label = _("Details Card")
        template = "pages/blocks/card_detail_block.html"


class CardSimpleBlock(CardWithImageBlockBase):
    class Meta:
        icon = "user"
        label = _("Simple Card")
        template = "pages/blocks/card_simple_block.html"


class IconBulletBlock(blocks.StructBlock):
    icon = blocks.CharBlock()
    text = blocks.CharBlock()

    class Meta:
        icon = "user"
        label = _("Icons Bullet Points")
        template = "pages/blocks/icon_bullet_block.html"


class BlocksStreamBlock(blocks.StreamBlock):
    """The stream block with all components"""

    simple_card = CardSimpleBlock()
    detail_card = CardDetailBlock()
    bullet_points = IconBulletBlock()


class SingleColumnBlock(blocks.StructBlock):
    """Struct Block for a single row section"""

    background_color = blocks.ChoiceBlock(choices=ColorChoices.choices)
    text_color = blocks.ChoiceBlock(choices=TextColorChoices.choices)
    column = blocks.StreamBlock(
        [
            ("simple_card", CardSimpleBlock()),
            ("detail_card", CardDetailBlock()),
            ("icon_bullets", IconBulletBlock()),
            ("rich_text", blocks.RichTextBlock()),
        ],
        min_num=1,
    )

    class Meta:
        template = "pages/blocks/layout/single_column_block.html"


class TwoColumnBlock(blocks.StructBlock):
    """Struct block for two columns section"""

    background_color = blocks.ChoiceBlock(choices=ColorChoices.choices)
    text_color = blocks.ChoiceBlock(choices=TextColorChoices.choices)
    left = blocks.StreamBlock(
        [
            ("simple_card", CardSimpleBlock()),
            ("detail_card", CardDetailBlock()),
            ("icon_bullets", IconBulletBlock()),
            ("rich_text", blocks.RichTextBlock()),
        ],
        min_num=1,
    )
    right = blocks.StreamBlock(
        [
            ("simple_card", CardSimpleBlock()),
            ("detail_card", CardDetailBlock()),
            ("icon_bullets", IconBulletBlock()),
            ("rich_text", blocks.RichTextBlock()),
        ],
        min_num=1,
    )

    class Meta:
        template = "pages/blocks/layout/two_columns_block.html"


class HomePage(Page):
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("The image which shows in the hero header of the page."),
    )
    hero_tagline = models.CharField(
        verbose_name=_("Hero Tagline"),
        max_length=200,
        blank=True,
        help_text=_("The tag line which appears on the top part of the hero image."),
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
    content = StreamField(
        [("single_column", SingleColumnBlock()), ("tow_columns", TwoColumnBlock())],
        blank=True,
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel("hero_image"),
        FieldPanel("hero_tagline"),
        FieldPanel("hero_main_text"),
        FieldPanel("hero_subtext"),
        StreamFieldPanel("content"),
    ]

    def _str__(self):
        return f"{self.title}"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(
            {
                "customer_form": CustomerInformationForm(),
                "shipping_form": ShippingInformationForm(),
                "product_add_formset": formset_factory(ProductAddForm),
            }
        )
        return context
