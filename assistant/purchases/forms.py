import logging

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from assistant.products.models import Supplier
from assistant.orders.models import Order, LineItem
from .models import PurchaseOrder

from assistant.purchases.services import (
    process_add_to_purchase_order,
    process_purchase_order,
    receive_stock,
)

logger = logging.getLogger(__name__)


class PurchaseOrderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.variant = kwargs.pop("variant")
        super().__init__(**kwargs)

    supplier = forms.CharField(
        label=_("New Supplier"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    system_supplier = forms.ModelChoiceField(
        label=_("Existing Supplier"),
        queryset=Supplier.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    estimated_arrival = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    purchase_order = forms.ModelChoiceField(
        label=_("Purchase Order"),
        queryset=PurchaseOrder.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def save(self):
        if self.cleaned_data["purchase_order"]:
            obj = process_add_to_purchase_order(
                variant=self.variant, **self.cleaned_data
            )
        else:
            obj = process_purchase_order(
                variant=self.variant, **self.cleaned_data
            )
        return obj

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("system_supplier") and not cleaned_data.get(
            "supplier"
        ):
            raise forms.ValidationError(
                _(
                    "Invalid value: One of the Supplier Fields should be provided"
                ),
                code="invalid",
            )


class ReceiveItemForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop("item")
        super().__init__(**kwargs)

    quantity = forms.IntegerField()

    def save(self):
        item = receive_stock(
            item=self.item, quantity=self.cleaned_data['quantity']
        )
        return item
