from django.urls import path

from .views import WebhookView, StreamListView

app_name = "shopify_sync"

urlpatterns = [
    path("webhook/", WebhookView.as_view(), name="shopify-webhook-view"),
    path("events/", StreamListView.as_view(), name="shopify-stream-view")
]
