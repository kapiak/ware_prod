from django.urls import path

from .views import (
    line_items_for_variant,
    line_item_stock,
    # allocate_stock_to_line,
)

app_name = "warehouse"

urlpatterns = [
    path(
        "line-items/<uuid:variant>/",
        line_items_for_variant,
        name="allocate_stock_to_line_item",
    ),
    path(
        'product-orders-modal/<uuid:line_item>/',
        line_item_stock,
        name='product_stock_modal_workflow',
    ),
    # path('allocate/', allocate_stock_to_line, name='allocate_stock_to_line'),
]
