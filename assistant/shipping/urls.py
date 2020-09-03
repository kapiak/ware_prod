from django.urls import path

from .views import ShipmentListView, ShipmentDetailView

app_name = "shipping"

urlpatterns = [
    path("", ShipmentListView.as_view(), name="shipment_list"),
    path("<uuid:guid>/", ShipmentDetailView.as_view(), name="shipment_detail")
]
