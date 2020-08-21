from django.urls import path

from .views import (
    get_product_by_link,
    get_product_by_link_sync,
    checkout,
    add_to_purchase_order,
    mark_purchase_item_received,
    CustomerOrderList,
)

app_name = "weblink_channel"

urlpatterns = [
    path("scrape/", get_product_by_link, name="get_product_by_link"),
    path("sync-scrape/", get_product_by_link_sync, name="get_product_by_link_sync",),
    path("checkout/", checkout, name="checkout"),
    path(
        "add-to-purchase/<uuid:item_uuid>",
        add_to_purchase_order,
        name="add_to_purchase_order",
    ),
    path(
        "mark_purchase_item_received/<uuid:item_uuid>",
        mark_purchase_item_received,
        name="mark_purchase_item_received",
    ),
    path("customer-orders/", CustomerOrderList.as_view(), name="customer_order_list"),
]
