from django.urls import path

from .views import product_orders_modal

app_name = "products"

urlpatterns = [
    path(
        'product-orders-modal/<uuid:guid>/',
        product_orders_modal,
        name='product_orders_modal_workflow',
    )
]
