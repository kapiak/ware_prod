from django.urls import path

from .views import (
    get_product_by_link,
    get_product_by_link_sync,
    checkout,
    CustomerOrderList,
    CustomerOrderDetail,
    CustomerOrderCreate,
    CustomerProductVariantListView,
    CustomerProductVariantDetailView,
    checkout_api_view,
)

app_name = "weblink_channel"

urlpatterns = [
    path("scrape/", get_product_by_link, name="get_product_by_link"),
    path("sync-scrape/", get_product_by_link_sync, name="get_product_by_link_sync",),
    path("checkout/", checkout, name="checkout"),
    path("checkout-api/", checkout_api_view, name="checkout-api-view"),
    path("guest-checkout-api/", checkout_api_view, name="guest-checkout-api-view"),
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
    path(
        "customer-products/",
        CustomerProductVariantListView.as_view(),
        name="customer_product_list",
    ),
    path(
        "customer-products/<uuid:guid>/",
        CustomerProductVariantDetailView.as_view(),
        name="customer_product_detail",
    ),
]
