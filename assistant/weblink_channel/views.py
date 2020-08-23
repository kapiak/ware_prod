import io
import json
import logging
import uuid

import aiohttp
import requests
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
from django.views.generic import DetailView, ListView, TemplateView
from rest_framework import status
from rest_framework.parsers import JSONParser
from wagtail.admin import messages
from wagtail.admin.modal_workflow import render_modal_workflow

from assistant.orders.models import Order
from assistant.orders.services import process_order, process_order_for_user

from .serializers import CartSerializer, ProductURLSerializer, UserCartSerializer

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
                    # data = await extract_metadata(
                    #     response_data, serializer.data["link"]
                    # )
                    # data.update(data)
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
            # data = extract_metadata_sync(response.text, serializer.data["link"])
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


class CustomerOrderDetail(LoginRequiredMixin, DetailView):
    template_name = "weblink_channel/orders/detail.html"
    queryset = Order.objects.all()
    context_object_name = "order"
    slug_field = "guid"
    slug_url_kwarg = "guid"

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class CustomerOrderCreate(LoginRequiredMixin, TemplateView):
    template_name = "weblink_channel/orders/form.html"


def checkout(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        data = JSONParser().parse(request)
        serializer_class = CartSerializer()
        if request.user.is_authenticated:
            serializer_class = UserCartSerializer
            data["customer"].update(
                {"name": request.user.fullname, "email": request.user.email}
            )
            serializer = serializer_class(data=data)
            if serializer.is_valid():
                process_order_for_user(user=request.user, **serializer.data)
                return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse(
                serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        serializer = serializer_class(data=data)
        if serializer.is_valid():
            try:
                process_order(**serializer.data)
            except ValidationError as eae:
                return JsonResponse(
                    {"message": eae.message, "code": eae.code},
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(
            serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    return JsonResponse({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
