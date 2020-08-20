import uuid

from django.core.paginator import Paginator
from django.http import JsonResponse, HttpRequest
from django.db.models import F, Sum, Q
from django.shortcuts import render, get_object_or_404

from wagtail.admin.modal_workflow import render_modal_workflow

from assistant.orders.models import Order, LineItem
from assistant.products.models import Product, ProductVariant
from assistant.purchases.models import PurchaseOrder, PurchaseOrderItem
from assistant.purchases.forms import PurchaseOrderForm
from assistant.warehouse.forms import SimpleAllocationForm, StockReceiveForm


def product_orders_modal(request, guid: uuid.UUID) -> JsonResponse:
    page_query = int(request.GET.get("page", 1))
    variants = get_object_or_404(Product, guid=guid).variants.all()
    order_lines = LineItem.objects.filter(variant__in=variants)
    qs = Paginator(Order.objects.filter(lines__in=order_lines).distinct(), 2)
    return render_modal_workflow(
        request,
        "products/choosers/orders_list.html",
        None,
        {"paginator": qs, "page": qs.page(page_query), "product_guid": guid,},
        json_data={"step": "chooser"},
    )


def make_product_purchase(request: HttpRequest, guid: uuid.UUID) -> JsonResponse:
    page_query = int(request.GET.get("page", 1))
    variant = ProductVariant.objects.prefetch_related("order_lines").get(guid=guid)
    purchase_orders = PurchaseOrder.objects.filter(
        status=PurchaseOrder.StatusChoices.DRAFT
    )
    paginator = Paginator(purchase_orders, 5)
    qs = variant.order_lines.aggregate(total_qty=Sum("quantity"))
    if request.method == "POST":
        form = PurchaseOrderForm(data=request.POST, variant=variant)
        if form.is_valid():
            obj = form.save()
            return render_modal_workflow(
                request, None, None, {"obj": obj}, json_data={"step": "created"}
            )
        return render_modal_workflow(
            request,
            "products/choosers/product_purchase.html",
            None,
            {
                "obj": variant,
                "page": paginator.page(page_query),
                "purchase_orders": purchase_orders,
                "form": form,
                "form_errors": form.errors,
            },
            json_data={"step": "chooser"},
        )
    to_purchase = (
        variant.needed_stock["quantity"]
        or 0 - variant.available_stock["quantity"]
        or 0 - variant.in_purchase["quantity"]
        or 0
    )
    form = PurchaseOrderForm(initial={"quantity": to_purchase}, variant=variant)
    return render_modal_workflow(
        request,
        "products/choosers/product_purchase.html",
        None,
        {
            "obj": variant,
            "page": paginator.page(page_query),
            "purchase_orders": purchase_orders,
            "form": form,
        },
        json_data={"step": "chooser"},
    )


def allocate_product_to_order(request: HttpRequest, guid: uuid.UUID) -> JsonResponse:
    variant = ProductVariant.objects.prefetch_related("order_lines").get(guid=guid)
    if request.method == "POST":
        form = SimpleAllocationForm(request.POST, variant=variant)
        if form.is_valid():
            items = form.save()
            print(items)
            return render_modal_workflow(
                request,
                None,
                None,
                {"obj": variant, "assigned_to": items},
                json_data={"step": "allocated"},
            )
    form = SimpleAllocationForm(variant=variant, initial={"variant": variant})
    return render_modal_workflow(
        request,
        "products/choosers/product_allocation.html",
        None,
        {"obj": variant, "form": form},
        json_data={"step": "chooser"},
    )


def receive_product_stock(request: HttpRequest, guid: uuid.UUID) -> JsonResponse:
    variant = ProductVariant.objects.get(guid=guid)
    purchase_orders = PurchaseOrderItem.objects.filter(
        ~Q(sales_orders__order__status__in=[PurchaseOrderItem.StatusChoices.RECEIVED,]),
        Q(sales_orders__variant=variant),
    )
    print(purchase_orders)
    form = StockReceiveForm(variant=variant, purchase_orders=purchase_orders)
    return render_modal_workflow(
        request,
        "products/choosers/product_receive.html",
        None,
        {"obj": variant, "form": form},
        json_data={"step": "chooser"},
    )
