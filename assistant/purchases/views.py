import uuid

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import PurchaseOrder, PurchaseOrderItem
# from .services import receive_stock


class PurchaseListView(ListView):
    template_name = "purchases/list.html"
    queryset = PurchaseOrder.objects.all()
    context_object_name = "orders"
    paginate_by = 100

    def get_queryset(self):
        qs = super().get_queryset().select_related("supplier").prefetch_related("items")
        return qs


@api_view(["GET"])
def purchase_receive_endpoint(
    request: Request, item_guid: uuid.UUID, quantity: int
) -> Response:
    item = get_object_or_404(PurchaseOrderItem, guid=item_guid)
    # receive_stock(item=item, quantity=quantity)
    return Response({})
