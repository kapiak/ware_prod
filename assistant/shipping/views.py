import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import formset_factory, modelformset_factory
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from assistant.orders.models import Order

from .forms import PieceForm, ShipmentForm
from .models import Shipment, ShipmentLine


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


def shipping_form_view(request: HttpRequest, guid: uuid.UUID) -> HttpResponse:
    order = get_object_or_404(Order, guid=guid)
    template = "shipments/form.html"
    context = {
        "order": order,
    }
    return render(request, template, context)
