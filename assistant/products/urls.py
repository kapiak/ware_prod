from django.urls import path

from .views import (
    product_orders_modal,
    make_product_purchase,
    allocate_product_to_order,
    receive_product_stock,
)

app_name = "products"

urlpatterns = [
    path(
        "product-orders-modal/<uuid:guid>/",
        product_orders_modal,
        name="product_orders_modal_workflow",
    ),
    path(
        "products/make-purchase/<uuid:guid>",
        make_product_purchase,
        name="make_product_purchase",
    ),
    path(
        "products/allocation/<uuid:guid>/",
        allocate_product_to_order,
        name="allocate_product_to_order",
    ),
    path(
        "products/receive/<uuid:guid>/",
        receive_product_stock,
        name="receive_product_stock",
    ),
]
