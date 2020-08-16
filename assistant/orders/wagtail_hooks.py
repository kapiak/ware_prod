from django.utils.translation import gettext_lazy as _

from wagtail.admin.edit_handlers import TabbedInterface, ObjectList, FieldPanel
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from .models import Order, LineItem


class OrderWagtailAdmin(ModelAdmin):
    model = Order
    menu_order = 100
    menu_icon = 'doc-empty'
    list_display = ('number', 'customer_email', 'customer_id', 'status')
    list_filter = ('status', 'cancel_reason')
    list_export = list_display

    panels = [
        FieldPanel('number'),
        MultiFieldPanel(
            [
                FieldPanel('customer_email'),
                FieldPanel('customer_id'),
                FieldPanel('user'),
            ],
            heading=_("Customer Details"),
        ),
        FieldPanel('type'),
        FieldPanel('status'),
        FieldPanel('closed_at'),
        MultiFieldPanel(
            [
                FieldPanel('total_price'),
                FieldPanel('subtotal_price'),
                FieldPanel('total_tax'),
            ],
            heading=_("Price Details"),
        ),
        MultiFieldPanel(
            [FieldPanel('cancel_reason'), FieldPanel('cancelled_at')],
            heading=_("Cancellation Details"),
        ),
    ]
    lines_panels = [
        InlinePanel(
            'lines',
            [
                FieldPanel('variant'),
                FieldPanel('is_shipping_required'),
                FieldPanel('quantity'),
                FieldPanel('quantity_fulfilled'),
            ],
            label=_("Line Items"),
        )
    ]
    edit_handler = TabbedInterface(
        [
            ObjectList(panels, heading=_("Main")),
            ObjectList(lines_panels, heading=_("Line Items")),
        ]
    )


class OrderWagtailAdminGroup(ModelAdminGroup):
    menu_label = _("Orders")
    menu_icon = 'list-ul'
    menu_order = 200
    items = (OrderWagtailAdmin,)


modeladmin_register(OrderWagtailAdminGroup)
