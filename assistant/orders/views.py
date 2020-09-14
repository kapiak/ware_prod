import uuid

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from assistant.products.models import ProductVariant
from assistant.purchases.forms import PurchaseOrderForm

from .models import Order


class OrderListView(ListView):
    template_name = "orders/list.html"
    queryset = Order.objects.all()
    context_object_name = "orders"
    paginate_by = 100

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related("lines", "lines__variant").select_related("user")
        return qs


def add_to_purchase_modal(request: HttpRequest, guid: uuid.UUID) -> HttpResponse:
    template_name = "core/modal.html"
    variant = get_object_or_404(ProductVariant, guid=guid)
    context = {
        "title": _("Add To Purchase Order"),
        "action": reverse("orders:add_to_purchase_modal", kwargs={'guid': variant.guid}),
    }
    if request.method == 'POST':
        form = PurchaseOrderForm(variant=variant, data=request.POST)
        if form.is_valid():
            form.save()
            context.update({
                'valid': True,
                'title': _("Added to Purchase Order")
            })
            return JsonResponse(context)
        context.update({
            "valid": False,
            "form": form
        })
        return render(request, template_name, context)
    context.update({
        "form": PurchaseOrderForm(variant=variant)
    })
    return render(request, template_name, context)
