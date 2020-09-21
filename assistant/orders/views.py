import uuid

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q

from assistant.products.models import ProductVariant
from assistant.purchases.forms import PurchaseOrderForm

from .models import Order


class OrderListView(ListView):
    template_name = "orders/list.html"
    queryset = Order.objects.all()
    context_object_name = "orders"
    paginate_by = 100

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .prefetch_related("lines", "lines__variant")
            .select_related("user")
        )
        query = self.request.GET.get('q', None)
        if query:
            qs = qs.filter(
                Q(number__startswith=query)
                | Q(metadata__shopify_id__startswith=query)
                | Q(metadata__shopify_order_number__startswith=query)
                | Q(lines__variant__metadata__shopify_id__startswith=query)
            ).order_by('-created_at')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'q': self.request.GET.get('q', None)})
        return context


def order_search(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', None)
    page = request.GET.get('page', None)
    qs = Order.objects.all()
    if query:
        qs = Order.objects.filter(
            Q(number__startswith=query)
            | Q(metadata__shopify_id__startswith=query)
            | Q(metadata__shopify_order_number__startswith=query)
            | Q(lines__variant__metadata__shopify_id__startswith=query)
        ).order_by('-created_at')
    paginator = Paginator(qs, 10)
    if page:
        page_obj = paginator.page(page)
    else:
        page_obj = paginator.page(1)
    context = {
        'orders': page_obj.object_list,
        'page_obj': page_obj,
        'q': query,
    }
    return render(request, "orders/includes/table_list.html", context)


def add_to_purchase_modal(
    request: HttpRequest, guid: uuid.UUID
) -> HttpResponse:
    template_name = "core/modal.html"
    variant = get_object_or_404(ProductVariant, guid=guid)
    context = {
        "title": _("Add To Purchase Order"),
        "action": reverse(
            "orders:add_to_purchase_modal", kwargs={'guid': variant.guid}
        ),
    }
    if request.method == 'POST':
        form = PurchaseOrderForm(variant=variant, data=request.POST)
        if form.is_valid():
            form.save()
            context.update(
                {'valid': True, 'title': _("Added to Purchase Order")}
            )
            return JsonResponse(context)
        context.update({"valid": False, "form": form})
        return render(request, template_name, context)
    context.update({"form": PurchaseOrderForm(variant=variant)})
    return render(request, template_name, context)
