from django.urls import path

from .views import ShipmentListView, ShipmentDetailView, get_dhl_rate, shipping_item_detail_modal

app_name = "shipping"

urlpatterns = [
    path("", ShipmentListView.as_view(), name="shipment_list"),
    path("<uuid:guid>/", ShipmentDetailView.as_view(), name="shipment_detail"),
    path("modal/<uuid:guid>/", shipping_item_detail_modal, name="shipping_item_detail_modal"),
    path("rates/hdl/", get_dhl_rate, name="get_dhl_rate"),
]
