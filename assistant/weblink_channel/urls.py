from django.urls import path

from .views import (
    get_product_by_link,
    get_product_by_link_sync,
    checkout,
    add_to_purchase_order,
    mark_pruchase_item_recieved,
)

app_name = "weblink_channel"

urlpatterns = [
    path("scrape/", get_product_by_link, name="get_product_by_link"),
    path(
        "sync-scrape/",
        get_product_by_link_sync,
        name="get_product_by_link_sync",
    ),
    path("checkout/", checkout, name="checkout"),
    path(
        "add-to-pruchase/<uuid:item_uuid>",
        add_to_purchase_order,
        name="add_to_purchase_order",
    ),
    path(
        "mark_pruchase_item_recieved/<uuid:item_uuid>",
        mark_pruchase_item_recieved,
        name="mark_pruchase_item_recieved",
    ),
]
