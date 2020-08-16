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
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin

from .models import Vendor, Product, ProductVariant
from .helpers import ProductButtonHelper, ProductVariantButtonHelper


class VendorWagtailAdmin(ModelAdmin):
    model = Vendor
    menu_icon = "user"
    menu_order = 100


class ProductWagtailAdmin(ModelAdmin):
    model = Product
    menu_icon = "tag"
    menu_order = 200
    inspect_view_enabled = True
    inspect_template_name = "products/inspect.html"
    list_select_related = True
    list_display = ("title", "max_price", "min_price", "vendor")
    list_filter = ("vendor",)
    search_fields = ("title", "product_type__name", "description")
    list_export = (
        "title",
        "sku",
        "max_price",
        "min_price",
        "vendor",
        "product_type",
    )
    button_helper_class = ProductButtonHelper
    index_view_extra_js = [
        "wagtailadmin/js/modal-workflow.js",
        "js/related-orders.js",
    ]

    panels = [
        FieldPanel("vendor"),
        FieldPanel("title", classname="full title"),
        FieldPanel("slug"),
        FieldPanel("description", classname="full"),
        FieldPanel("weight"),
        MultiFieldPanel(
            [FieldPanel("max_price"), FieldPanel("min_price")],
            heading="Prices",
        ),
    ]
    variant_panel = [
        InlinePanel(
            "variants",
            [
                FieldPanel("sku"),
                FieldPanel("barcode"),
                FieldPanel("name"),
                FieldPanel("price"),
                FieldPanel("cost_price"),
                FieldPanel("weight"),
            ],
            label=_("Variants"),
        )
    ]
    edit_handler = TabbedInterface(
        [
            ObjectList(panels, heading=_("General")),
            ObjectList(variant_panel, heading=_("Variants")),
        ]
    )

    def get_queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site.
        """
        qs = (
            self.model._default_manager.get_queryset()
            .select_related("vendor", "product_type")
            .prefetch_related("variants")
        )
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class ProductVariantWagtailAdmin(ThumbnailMixin, ModelAdmin):
    model = ProductVariant
    menu_icon = "tick"
    menu_order = 300
    inspect_view_enabled = True
    list_per_page = 20
    list_display_add_buttons = "sku"
    list_display = ("get_first_image", "sku", "barcode", "name", "price")
    # list_filter = ('product', 'price', 'cost_price', 'weight')
    search_fields = ("sku", "barcode", "name")
    button_helper_class = ProductVariantButtonHelper
    thumb_image_field_name = "Image"
    index_view_extra_js = [
        "wagtailadmin/js/modal-workflow.js",
        "js/related_line_items.js",
    ]

    panels = [
        MultiFieldPanel(
            [FieldPanel("sku"), FieldPanel("barcode")], heading=_("Identity")
        ),
        FieldPanel("name"),
        MultiFieldPanel(
            [FieldPanel("price"), FieldPanel("cost_price")],
            heading=_("Prices"),
        ),
        FieldPanel("weight"),
    ]


class ProductWagtailAdminGroup(ModelAdminGroup):
    menu_label = _("Products")
    menu_icon = "tag"
    menu_order = 100
    items = (
        VendorWagtailAdmin,
        ProductWagtailAdmin,
        ProductVariantWagtailAdmin,
    )


modeladmin_register(ProductWagtailAdminGroup)
