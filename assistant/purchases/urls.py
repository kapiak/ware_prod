from django.urls import path
from .views import PurchaseListView, recieve_item

app_name = "purchases"

urlpatterns = [
    path("", PurchaseListView.as_view(), name="purchase-order-list"),
    path("<uuid:guid>/", recieve_item, name="receive-item"),
]
