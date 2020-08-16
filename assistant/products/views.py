import uuid

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from wagtail.admin.modal_workflow import render_modal_workflow

from assistant.orders.models import Order, LineItem
from assistant.products.models import Product


def product_orders_modal(request, guid: uuid.UUID) -> JsonResponse:
    page_query = int(request.GET.get('page', 1))
    variants = get_object_or_404(Product, guid=guid).variants.all()
    order_lines = LineItem.objects.filter(variant__in=variants)
    qs = Paginator(Order.objects.filter(lines__in=order_lines).distinct(), 2)
    return render_modal_workflow(
        request,
        'products/choosers/orders_list.html',
        None,
        {'paginator': qs, 'page': qs.page(page_query), 'product_guid': guid},
        json_data={'step': 'chooser'},
    )
