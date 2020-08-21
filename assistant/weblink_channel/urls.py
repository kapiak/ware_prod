from django.urls import path

from .views import (
    get_product_by_link,
    get_product_by_link_sync,
    checkout,
    CustomerOrderList,
    CustomerOrderDetail,
    CustomerOrderCreate,
)

app_name = "weblink_channel"

urlpatterns = [
    path("scrape/", get_product_by_link, name="get_product_by_link"),
    path("sync-scrape/", get_product_by_link_sync, name="get_product_by_link_sync",),
    path("checkout/", checkout, name="checkout"),
    path("customer-orders/", CustomerOrderList.as_view(), name="customer_order_list"),
    path(
        "customer-orders/<uuid:guid>/",
        CustomerOrderDetail.as_view(),
        name="customer_order_detail",
    ),
    path(
        "customer-orders/new/",
        CustomerOrderCreate.as_view(),
        name="customer_order_create",
    ),
]
