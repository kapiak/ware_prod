from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.urls import re_path

from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.admin.edit_handlers import TabbedInterface, ObjectList, FieldPanel
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from .models import PurchaseOrder


class PurchaseOrderWagtailAdmin(ModelAdmin):
    model = PurchaseOrder
    menu_label = _("Purchase Orders")
    menu_icon = "tag"
    menu_order = 200
    list_display = ("number", "status", "estimated_arrival", "supplier", "created_at")
    list_filter = ("status",)
    edit_template_name = "weblink_channel/modeladmin/edit.html"
    receive_view_extra_css = []

    panels = [
        FieldPanel("number", classname="title"),
        FieldPanel("estimated_arrival"),
        FieldPanel("supplier"),
        FieldPanel("status"),
        InlinePanel(
            "items", [FieldPanel("status"), FieldPanel("quantity")], label=_("Items"),
        ),
    ]

    edit_handlers = TabbedInterface([ObjectList(panels, heading=_("Details"))])


modeladmin_register(PurchaseOrderWagtailAdmin)
