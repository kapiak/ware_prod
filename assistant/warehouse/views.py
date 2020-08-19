import uuid
import logging

from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.forms import formset_factory

from wagtail.admin.modal_workflow import render_modal_workflow
from assistant.orders.models import LineItem
from assistant.products.models import ProductVariant
from .models import Stock
from .forms import AllocationForm
from .exceptions import InsufficientStock

logger = logging.getLogger(__name__)


def line_items_for_variant(request: HttpRequest, variant: uuid.UUID) -> JsonResponse:
    """Return the json response for the modal render."""
    variant = get_object_or_404(ProductVariant, guid=variant)
    line_items = LineItem.objects.filter(variant=variant).prefetch_related(
        "allocations"
    )
    page_query = int(request.GET.get("page", 1))
    line_items_page = Paginator(line_items, page_query)
    return render_modal_workflow(
        request,
        "products/choosers/line_items.html",
        None,
        {"line_items_page": line_items_page},
        json_data={"step": "chooser"},
    )


def line_item_stock(request: HttpRequest, line_item: uuid.UUID) -> JsonResponse:
    """Returns the json to render in the modal."""
    line_item = get_object_or_404(LineItem, guid=line_item)
    stock_queryset = Stock.objects.annotate_available_quantity().filter(
        product_variant=line_item.variant
    )
    AllocationFormSet = formset_factory(AllocationForm, extra=0)

    if request.method == "POST":
        formset = AllocationFormSet(data=request.POST)
        if formset.is_valid():
            for form in formset:
                try:
                    form.save()
                except InsufficientStock as ins:
                    logger.exception("No stock %s" % ins)

    formset = AllocationFormSet(
        initial=[
            {
                "warehouse": stock.warehouse,
                "stock": stock.guid,
                "order_line": line_item.guid,
                "quantity": stock.available_quantity,
            }
            for stock in stock_queryset
            if stock.available_quantity
        ]
    )
    return render_modal_workflow(
        request,
        "products/choosers/stock.html",
        None,
        {"stock": stock_queryset, "line_item": line_item, "formset": formset},
        json_data={"step": "allocation"},
    )
