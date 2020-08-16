from django.utils.translation import gettext_lazy as _

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from .models import Address


class AddressWagtailAdmin(ModelAdmin):
    model = Address
    menu_icon = "house"
    menu_label = _("addresses")

    panels = [
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("company_name"),
        FieldPanel("street_address_1"),
        FieldPanel("street_address_2"),
        FieldPanel("city"),
        FieldPanel("city_area"),
        FieldPanel("postal_code"),
        FieldPanel("country"),
        FieldPanel("country_area"),
        FieldPanel("phone"),
    ]
