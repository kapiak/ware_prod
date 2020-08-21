import io
import json
import logging
import uuid

import aiohttp
import requests
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.functional import cached_property
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from rest_framework import status
from rest_framework.parsers import JSONParser
from wagtail.admin import messages
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.contrib.modeladmin.views import EditView, InstanceSpecificView

from assistant.orders.models import Order
from assistant.orders.services import process_order

from .forms import PurchaseOrderAddForm, PurchaseOrderForm, PurchaseOrderItemReceiveForm
from .helpers import (
    EmailAlreadyExists,
    extract_metadata,
    extract_metadata_sync,
    process_weblink_checkout,
    submit_order_for_purchase,
)
from .models import PurchaseOrder, PurchaseOrderItem, WebLinkOrderItem
from .serializers import CartSerializer, ProductURLSerializer

logger = logging.getLogger(__name__)


User = get_user_model()


@transaction.non_atomic_requests
async def get_product_by_link(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        serializer = ProductURLSerializer(data=JSONParser().parse(request))
        if serializer.is_valid():
            data = {}
            async with aiohttp.ClientSession() as session:
                async with session.get(serializer.data["link"]) as resp:
                    logger.info("initiated session to call endpoint")
                    response_data = await resp.text()
                    logger.info("Processing the response")
                    data = await extract_metadata(
                        response_data, serializer.data["link"]
                    )
                    data.update(data)
            return JsonResponse(data)
        return JsonResponse(
            serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return JsonResponse(
        {"message": _("This endpoint accepts POST requests only.")},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


def get_product_by_link_sync(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        serializer = ProductURLSerializer(data=JSONParser().parse(request))
        if serializer.is_valid():
            data = {}
            response = requests.get(serializer.data["link"])
            data = extract_metadata_sync(response.text, serializer.data["link"])
            data.update(data)
            return JsonResponse(data)
        return JsonResponse(
            serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return JsonResponse(
        {"message": _("This endpoint accepts POST requests only.")},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


class CustomerOrderList(LoginRequiredMixin, ListView):
    template_name = "weblink_channel/orders/list.html"
    queryset = Order.objects.all()
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


def checkout(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        data = JSONParser().parse(request)
        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            try:
                # process_weblink_checkout(**serializer.data)
                process_order(**serializer.data)
            except EmailAlreadyExists as eae:
                return JsonResponse(
                    {"message": eae.message, "code": eae.code},
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(
            serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def add_to_purchase_order(request: HttpRequest, item_uuid: uuid.UUID) -> JsonResponse:
    page_query = int(request.GET.get("page", 1))
    item = get_object_or_404(WebLinkOrderItem, guid=item_uuid)
    form = PurchaseOrderForm(initial={"quantity": item.quantity})
    if request.method == "POST":
        if request.POST.get("add_type", None) == "to_existing":
            form = PurchaseOrderAddForm(request.POST)
            if form.is_valid():
                try:
                    obj = form.save(item=item)
                    return render_modal_workflow(
                        request,
                        None,
                        None,
                        {"purchase_order": obj},
                        json_data={"step": "choosen"},
                    )
                except IntegrityError as ie:
                    logger.info(f"PurchaseOrder already exists {ie}")
                    return render_modal_workflow(
                        request, None, None, json_data={"step": "choosen_already"},
                    )
            return render_modal_workflow(
                request, None, None, json_data={"step": "choosen"}
            )
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            try:
                obj = form.save(item=item)
                return render_modal_workflow(
                    request,
                    None,
                    None,
                    {"purchase_order": obj},
                    json_data={"step": "choosen"},
                )
            except IntegrityError as ie:
                logger.info(f"PurchaseOrder already exists {ie}")
                return render_modal_workflow(
                    request, None, None, json_data={"step": "choosen_already"}
                )
        return JsonResponse(
            {"errors": form.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    purchase_orders = PurchaseOrder.objects.filter(
        status=PurchaseOrder.StatusChoices.DRAFT
    )
    qs = Paginator(purchase_orders, 5)
    return render_modal_workflow(
        request,
        "weblink_channel/choosers/purchase_orders_list.html",
        None,
        {"paginator": qs, "page": qs.page(page_query), "form": form, "item": item,},
        json_data={"step": "chooser"},
    )


class PurchaseOrderEditView(EditView):
    @cached_property
    def submit_url(self):
        return self.url_helper.get_action_url("submit", self.pk_quoted)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "user_can_submit": self.permission_helper.user_can_submit_obj(
                    self.request.user, self.instance
                )
            }
        )
        return super().get_context_data(**context)

    def get_submit_message(self, instance):
        return _("%(model_name)s '%(instance)s' Submitted.") % {
            "model_name": capfirst(self.opts.verbose_name),
            "instance": instance,
        }

    def form_valid(self, form):
        if "action-submit" in self.request.POST:
            instance = submit_order_for_purchase(self.instance)
            messages.success(
                self.request, self.get_submit_message(instance),
            )
            return redirect(self.get_success_url())

        instance = form.save()
        messages.success(
            self.request,
            self.get_success_message(instance),
            buttons=self.get_success_message_buttons(instance),
        )
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.validation_error(self.request, self.get_error_message(), form)
        return self.render_to_response(self.get_context_data())


class PurchaseOrderReceiveView(InstanceSpecificView):
    template_name = "weblink_channel/modeladmin/receive.html"

    @property
    def media(self):
        return forms.Media(
            css={"all": self.model_admin.get_receive_view_extra_css()},
            js=self.model_admin.get_receive_view_extra_js(),
        )


def mark_purchase_item_received(
    request: HttpRequest, item_uuid: uuid.UUID
) -> JsonResponse:
    item = get_object_or_404(PurchaseOrderItem, guid=item_uuid)
    if request.method == "POST":
        logger.debug(f"Post request with data: {request.POST}")
        form = PurchaseOrderItemReceiveForm(request.POST)
        if form.is_valid():
            logger.debug("the form is valid")
            try:
                obj = form.save(item=item)
                logger.debug(f"form is saved and returned {obj.guid}")
                return render_modal_workflow(
                    request,
                    "weblink_channel/choosers/receive_purchased_item.html",
                    None,
                    {"item": item, "obj": obj},
                    json_data={"step": "marked"},
                )
            except forms.ValidationError as ve:
                logger.debug(f" Validation error with: {ve}")
                return render_modal_workflow(
                    request,
                    "weblink_channel/choosers/receive_purchased_item.html",
                    None,
                    {"item": item, "form": form},
                    json_data={"step": "invalid"},
                )
        logger.debug(f"the form is not valid and the errors are: {form.errors}")
        return render_modal_workflow(
            request,
            "weblink_channel/choosers/receive_purchased_item.html",
            None,
            {"item": item, "form": form},
            json_data={"step": "invalid"},
        )
    logger.debug("Its a get request")
    form = PurchaseOrderItemReceiveForm(initial={"quantity": item.quantity})
    return render_modal_workflow(
        request,
        "weblink_channel/choosers/receive_purchased_item.html",
        None,
        {"item": item, "form": form},
        json_data={"step": "chooser"},
    )
