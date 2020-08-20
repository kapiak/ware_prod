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

from .helpers import (
    WeblinkOrderItemButtonHelper,
    PurchaseOrderButtonHelper,
    PurchaseOrderPermissionHelper,
)
from .models import WebLinkOrder, WebLinkOrderItem, PurchaseOrder
from .views import PurchaseOrderReceiveView, PurchaseOrderEditView


class WebLinkOrderWagtilAdmin(ModelAdmin):
    model = WebLinkOrder
    menu_label = _("Orders")
    menu_icon = "tag"
    menu_order = 100
    list_display = ("number", "customer")
    search_fields = ("number", "customer")

    panels = [
        FieldPanel("number"),
        FieldPanel("customer"),
        FieldPanel("shipping_method"),
        FieldPanel("weight"),
    ]
    lines_panels = [
        FieldPanel("url"),
        FieldPanel("name"),
        FieldPanel("provided_price"),
        FieldPanel("quantity"),
        FieldPanel("weight"),
        FieldPanel("comments"),
    ]

    edit_handlers = TabbedInterface(
        [
            ObjectList(panels, heading=_("Order Information")),
            ObjectList(lines_panels, heading=_("Line Items")),
        ]
    )


class WebLinkOrderItemWagtailAdmin(ModelAdmin):
    model = WebLinkOrderItem
    menu_label = _("Ordered Products")
    menu_icon = "tag"
    list_display = (
        "url",
        "name",
        "provided_price",
        "quantity",
        "weight",
        "status",
        "variant",
        "created_at",
    )
    list_filter = ("status",)
    button_helper_class = WeblinkOrderItemButtonHelper
    index_view_extra_js = [
        "wagtailadmin/js/modal-workflow.js",
        "js/weblink-order-item-purchase.js",
    ]


class PurchaseOrderWagtailAdmin(ModelAdmin):
    model = PurchaseOrder
    menu_label = _("Purchase Orders")
    menu_icon = "tag"
    menu_order = 200
    list_display = ("number", "status", "estimated_arrival", "supplier")
    list_filter = ("status",)
    button_helper_class = PurchaseOrderButtonHelper
    permission_helper_class = PurchaseOrderPermissionHelper
    edit_template_name = "weblink_channel/modeladmin/edit.html"
    edit_view_class = PurchaseOrderEditView
    receive_view_class = PurchaseOrderReceiveView
    receive_view_extra_js = [
        "wagtailadmin/js/modal-workflow.js",
        "js/purchase-order-receive.js",
    ]
    receive_view_extra_css = []

    @cached_property
    def receive_url(self):
        return self.url_helper.get_action_url("receive", self.pk_quoted)

    def get_receive_view_extra_js(self):
        return self.receive_view_extra_js

    def get_receive_view_extra_css(self):
        return self.receive_view_extra_css

    def receive_view(self, request, instance_pk):
        """
        Instantiates a class-based view to provide 'edit' functionality for the
        assigned model, or redirect to Wagtail's edit view if the assigned
        model extends 'Page'. The view class used can be overridden by changing
        the  'edit_view_class' attribute.
        """
        kwargs = {"model_admin": self, "instance_pk": instance_pk}
        view_class = self.receive_view_class
        return view_class.as_view(**kwargs)(request)

    def get_admin_urls_for_registration(self):
        urls = (
            re_path(
                self.url_helper.get_action_url_pattern("index"),
                self.index_view,
                name=self.url_helper.get_action_url_name("index"),
            ),
            re_path(
                self.url_helper.get_action_url_pattern("create"),
                self.create_view,
                name=self.url_helper.get_action_url_name("create"),
            ),
            re_path(
                self.url_helper.get_action_url_pattern("edit"),
                self.edit_view,
                name=self.url_helper.get_action_url_name("edit"),
            ),
            re_path(
                self.url_helper.get_action_url_pattern("delete"),
                self.delete_view,
                name=self.url_helper.get_action_url_name("delete"),
            ),
            re_path(
                self.url_helper.get_action_url_pattern("receive"),
                self.receive_view,
                name=self.url_helper.get_action_url_name("receive"),
            ),
        )
        return urls

    panels = [
        FieldPanel("number", classname="title"),
        FieldPanel("estimated_arrival"),
        FieldPanel("supplier"),
        FieldPanel("status"),
        InlinePanel(
            "items",
            [FieldPanel("sales_order_item"), FieldPanel("quantity")],
            label=_("Items"),
        ),
    ]

    edit_handlers = TabbedInterface([ObjectList(panels, heading=_("Details"))])


class WebLinkChannelWagtailAdminGroup(ModelAdminGroup):
    menu_label = _("Web Link Channel")
    menu_icon = "tag"
    menu_order = 200
    items = (WebLinkOrderItemWagtailAdmin,)


modeladmin_register(WebLinkChannelWagtailAdminGroup)
modeladmin_register(PurchaseOrderWagtailAdmin)
