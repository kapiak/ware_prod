import uuid

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from rest_framework.decorators import api_view
from django.http import HttpRequest, HttpResponse, JsonResponse

from .models import PurchaseOrder, PurchaseOrderItem
from .forms import ReceiveItemForm

from .services import receive_stock


class PurchaseListView(ListView):
    template_name = "purchases/list.html"
    queryset = PurchaseOrder.objects.all()
    context_object_name = "orders"
    paginate_by = 100

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("supplier")
            .prefetch_related("items")
        )
        return qs


def recieve_item(request: HttpRequest, guid: uuid.UUID) -> JsonResponse:
    print(request.POST)
    if request.method == 'POST':
        item = get_object_or_404(PurchaseOrderItem, guid=guid)
        form = ReceiveItemForm(item=item, data=request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'method not allowed'})
