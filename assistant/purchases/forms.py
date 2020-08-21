import logging

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from assistant.products.models import Supplier
from assistant.orders.models import Order, LineItem

from assistant.purchases.services import (
    process_add_to_purchase_order,
    process_purchase_order,
)

logger = logging.getLogger(__name__)


class PurchaseOrderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        variant = kwargs.pop("variant")
        super().__init__(**kwargs)
        self.fields["sales_orders"].queryset = LineItem.objects.filter(variant=variant)

    supplier = forms.CharField(label=_("Supplier"), required=False)
    system_supplier = forms.ModelChoiceField(
        label=_("Supplier"), queryset=Supplier.objects.all(), required=False
    )
    estimated_arrival = forms.IntegerField()
    quantity = forms.IntegerField()
    sales_orders = forms.ModelMultipleChoiceField(
        queryset=LineItem.objects.none(),
        help_text=_("Press Ctrl when selecting multiple sales orders"),
    )

    def save(self):
        obj = process_purchase_order(**self.cleaned_data)
        return obj

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("system_supplier") and not cleaned_data.get("supplier"):
            raise forms.ValidationError(
                _("Invalid value: One of the Supplier Fields should be provided"),
                code="invalid",
            )
