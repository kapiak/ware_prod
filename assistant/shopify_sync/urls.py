from django.urls import path

from .views import WebhookView

app_name = "shopify_sync"

urlpatterns = [
    path("webhook/", WebhookView.as_view(), name="shopify-webhook-view")
]
