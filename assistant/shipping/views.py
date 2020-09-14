import datetime
import logging
import uuid

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import formset_factory, modelformset_factory
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.views.generic import DetailView, ListView

from assistant.orders.models import Order

from .forms import PieceForm, ShipmentForm, ShipmentLineDetailForm
from .models import Shipment, ShipmentLine

logger = logging.getLogger(__name__)


class ShipmentListView(LoginRequiredMixin, ListView):
    template_name = "shipping/list.html"
    queryset = Shipment.objects.all()
    context_object_name = "shipments"
    paginate_by = 100


class ShipmentDetailView(LoginRequiredMixin, DetailView):
    template_name = "shipping/detail.html"
    queryset = Shipment.objects.all()
    context_object_name = "shipment"
    slug_field = "guid"
    slug_url_kwarg = "guid"


def shipping_item_detail_modal(request, guid: uuid.UUID) -> HttpResponse:
    item = get_object_or_404(ShipmentLine, guid=guid)
    context = {
        "item": item
    }
    if request.method == 'POST':
        form = ShipmentLineDetailForm(item=item, data=request.POST)
        if form.is_valid():
            form.save()
            context.pop('item')
            context.update({
                'valid': True,
                'title': _("Line item data has been updated.")
            })
            return JsonResponse(context)
        context.update({
            "valid": False,
            "form": form
        })
        return render(request, "shipping/modal_body.html", context)
    context.update({
        "form": ShipmentLineDetailForm(item=item, initial={'item': item})
    })
    return render(request, "shipping/modal_body.html", context)


def get_dhl_rate(request: HttpRequest) -> HttpResponse:
    request_xml_file = "shipping/xml/dhl/get_quote_request.xml"
    headers = {
        'Content-type':'application/x-www-form-urlencoded; charset=UTF-8',
        'futureDate': 'false',
        'languageCode':'PYTHON',
    }
    time = datetime.datetime.now().isoformat()
    print("Time: ", time)
    request_xml_data = render_to_string(request_xml_file, {'time': time})
    logger.info(request_xml_data)
    response = requests.post("https://xmlpi-ea.dhl.com/XMLShippingServlet", data=request_xml_data, headers=headers)
    logger.info(response.content)
    return HttpResponse(response.content)
