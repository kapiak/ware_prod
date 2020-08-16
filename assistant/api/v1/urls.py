from django.urls import include, path

app_name = "v1"

urlpatterns = [
    path("addresses/", include("assistant.addresses.api.v1.urls", namespace="addresses"))
]