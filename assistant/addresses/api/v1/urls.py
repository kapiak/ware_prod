from django.urls import path

from .views import AddressListCreateAPIView

app_name = "addresses"

urlpatterns = [
    path("", AddressListCreateAPIView.as_view(), name="address_list")
]