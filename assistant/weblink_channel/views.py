import json
import logging
import io
import aiohttp
import requests
import uuid

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.utils.functional import cached_property

from rest_framework.parsers import JSONParser
from rest_framework import status
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.contrib.modeladmin.views import (
    InstanceSpecificView,
    EditView,
    IndexView,
)

from .helpers import (
    extract_metadata,
    extract_metadata_sync,
    process_weblink_checkout,
    EmailAlreadyExists,
)
from .forms import PurchaseOrderForm, PurchaseOrderAddForm
from .serializers import ProductURLSerializer, CartSerializer
from .models import PurchaseOrder, WebLinkOrderItem, PurchaseOrderItem

logger = logging.getLogger(__name__)


@transaction.non_atomic_requests
async def get_product_by_link(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        serializer = ProductURLSerializer(data=JSONParser().parse(request))
        if serializer.is_valid():
            data = {}
            async with aiohttp.ClientSession() as session:
                async with session.get(serializer.data['link']) as resp:
                    logger.info("initiated session to call endpoint")
                    response_data = await resp.text()
                    logger.info("Processing the response")
                    data = await extract_metadata(
                        response_data, serializer.data['link']
                    )
                    data.update(data)
                    print("DATA: ", data)
            return JsonResponse(data)
        return JsonResponse(
            serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return JsonResponse(
        {'message': _("This endpoint accepts POST requests only.")},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


def get_product_by_link_sync(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        serializer = ProductURLSerializer(data=JSONParser().parse(request))
        if serializer.is_valid():
            data = {}
            response = requests.get(serializer.data['link'])
            data = extract_metadata_sync(
                response.text, serializer.data['link']
            )
            data.update(data)
            return JsonResponse(data)
        return JsonResponse(
            serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return JsonResponse(
        {'message': _("This endpoint accepts POST requests only.")},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


def checkout(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        data = JSONParser().parse(request)
        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            try:
                process_weblink_checkout(**serializer.data)
            except EmailAlreadyExists as eae:
                return JsonResponse(
                    {"message": eae.message, "code": eae.code},
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
            return JsonResponse(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return JsonResponse(
            serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def add_to_purchase_order(
    request: HttpRequest, item_uuid: uuid.UUID
) -> JsonResponse:
    page_query = int(request.GET.get('page', 1))
    item = get_object_or_404(WebLinkOrderItem, guid=item_uuid)
    form = PurchaseOrderForm(initial={'quantity': item.quantity})
    if request.method == 'POST':
        if request.POST.get('add_type', None) == 'to_existing':
            form = PurchaseOrderAddForm(request.POST)
            if form.is_valid():
                print("VAAAAAAAAAAAAAAAAAALiD")
                try:
                    obj = form.save(item=item)
                    return render_modal_workflow(
                        request,
                        None,
                        None,
                        {'purchase_order': obj},
                        json_data={'step': 'choosen'},
                    )
                except IntegrityError as ie:
                    logger.info(f"PurchaseOrder already exists {ie}")
                    return render_modal_workflow(
                        request,
                        None,
                        None,
                        json_data={'step': 'choosen_already'},
                    )
            print(form.errors)
            return render_modal_workflow(
                request, None, None, json_data={'step': 'choosen'}
            )
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            try:
                obj = form.save(item=item)
                return render_modal_workflow(
                    request,
                    None,
                    None,
                    {'pruchase_order': obj},
                    json_data={'step': 'choosen'},
                )
            except IntegrityError as ie:
                logger.info(f"PurchaseOrder already exists {ie}")
                return render_modal_workflow(
                    request, None, None, json_data={'step': 'choosen_already'}
                )
        return JsonResponse(
            {'errors': form.errors},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    purchase_orders = PurchaseOrder.objects.filter(
        status=PurchaseOrder.StatusChoices.DRAFT
    )
    qs = Paginator(purchase_orders, 5)
    return render_modal_workflow(
        request,
        'weblink_channel/choosers/purchase_orders_list.html',
        None,
        {
            'paginator': qs,
            'page': qs.page(page_query),
            'form': form,
            'item': item,
        },
        json_data={'step': 'chooser'},
    )


class PurchaseOrderEditView(EditView):
    @cached_property
    def submit_url(self):
        return self.url_helper.get_action_url('submit', self.pk_quoted)


class PurchaseOrderSubmitView(InstanceSpecificView):
    template_name = "weblink_channel/modeladmin/submit.html"
