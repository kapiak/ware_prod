from django.urls import path

from .views import OrderListView, order_search, add_to_purchase_modal

app_name = "orders"

urlpatterns = [
    path("", OrderListView.as_view(), name="order-list"),
    path('search/', order_search, name="order-search"),
    path(
        "add-to-purchase-modal/<uuid:guid>/",
        add_to_purchase_modal,
        name="add_to_purchase_modal",
    ),
]
