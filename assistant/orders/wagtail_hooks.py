from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from .helpers import OrderButtonHelper, OrderPermissionHelper, OrderUrlHelper
from .models import BatchOrderUpload, LineItem, Order


class OrderWagtailAdmin(ModelAdmin):
    model = Order
    menu_order = 100
    menu_icon = "doc-empty"
    list_display = ("number", "customer_email", "customer_id", "status")
    list_filter = ("status", "cancel_reason")
    list_export = list_display
    button_helper_class = OrderButtonHelper
    permission_helper_class = OrderPermissionHelper
    url_helper_class = OrderUrlHelper

    panels = [
        FieldPanel("number"),
        MultiFieldPanel(
            [
                FieldPanel("customer_email"),
                FieldPanel("customer_id"),
                FieldPanel("user"),
            ],
            heading=_("Customer Details"),
        ),
        FieldPanel("type"),
        FieldPanel("status"),
        FieldPanel("closed_at"),
        MultiFieldPanel(
            [FieldPanel("total_price"), FieldPanel("subtotal_price"),],
            heading=_("Price Details"),
        ),
        MultiFieldPanel(
            [FieldPanel("cancel_reason"), FieldPanel("cancelled_at")],
            heading=_("Cancellation Details"),
        ),
    ]
    lines_panels = [
        InlinePanel(
            "lines",
            [
                FieldPanel("variant"),
                FieldPanel("is_shipping_required"),
                FieldPanel("quantity"),
                FieldPanel("quantity_fulfilled"),
            ],
            label=_("Line Items"),
        )
    ]
    batch_panel = [
        InlinePanel("batches", [StreamFieldPanel("orders"),], label=_("Batch"))
    ]
    edit_handler = TabbedInterface(
        [
            ObjectList(panels, heading=_("Main")),
            ObjectList(lines_panels, heading=_("Line Items")),
            ObjectList(batch_panel, heading=_("Batch Upload Line Items")),
        ]
    )


class BatchOrderUploadWagtailAdmin(ModelAdmin):
    model = BatchOrderUpload
    menu_label = _("Batch Order")
    menu_icon = "tag"
    menu_order = 100

    panels = [
        StreamFieldPanel("orders"),
    ]


class OrderWagtailAdminGroup(ModelAdminGroup):
    menu_label = _("Orders")
    menu_icon = "list-ul"
    menu_order = 200
    items = (OrderWagtailAdmin, BatchOrderUploadWagtailAdmin)


modeladmin_register(OrderWagtailAdminGroup)
