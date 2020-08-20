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
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from .models import Warehouse, Stock, Allocation


class WarehouseWagtailAdmin(ModelAdmin):
    model = Warehouse
    menu_icon = "home"
    menu_order = 100
    list_display = ("name", "company_name", "email")
    search_fields = ("name", "company_name", "email")
    list_export = ("name", "company_name", "email")

    panels = [
        FieldPanel("name"),
        FieldPanel("company_name"),
        FieldPanel("email"),
        SnippetChooserPanel("address"),
    ]


class StockWagtailAdmin(ModelAdmin):
    model = Stock
    menu_icon = "table"
    menu_order = 200
    list_display = ("warehouse", "product_variant", "quantity")
    search_fields = ("warehouse", "product_variant")
    list_export = ("warehouse", "product_variant", "quantity")

    panels = [
        FieldPanel("warehouse"),
        FieldPanel("product_variant"),
        FieldPanel("quantity"),
    ]


class AllocationWagtailAdmin(ModelAdmin):
    model = Allocation
    menu_icon = "chain-broken"
    list_display = ("order_line", "stock", "quantity_allocated")
    menu_order = 300


class InventoryWagtailAdminGroup(ModelAdminGroup):
    menu_label = _("Inventory")
    menu_icon = "cogs"
    menu_order = 100
    items = (
        WarehouseWagtailAdmin,
        StockWagtailAdmin,
        AllocationWagtailAdmin,
    )


modeladmin_register(InventoryWagtailAdminGroup)
