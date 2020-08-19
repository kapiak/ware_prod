import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from assistant.products.models import Supplier
from .helpers import (
    process_purchase_order,
    process_add_to_purchase_order,
    process_recieve_purchase_order_item,
)
from .models import WebLinkOrderItem, PurchaseOrder, PurchaseOrderItem

logger = logging.getLogger(__name__)


class PurchaseOrderAddForm(forms.Form):
    purchase_order = forms.UUIDField()
    add_type = forms.CharField()

    def save(self, item: WebLinkOrderItem):
        obj = process_add_to_purchase_order(item=item, **self.cleaned_data)
        return obj

    def clean_purchase_order(self):
        data = self.cleaned_data['purchase_order']
        print(data)
        if not PurchaseOrder.objects.filter(guid=data).exists():
            raise forms.ValidationError(
                _("Invalid value: The PurchaseOrder Doesn't Exists"),
                code='invalid',
            )
        return data


class PurchaseOrderForm(forms.Form):
    supplier = forms.CharField(label=_("Supplier"), required=False)
    system_supplier = forms.ModelChoiceField(
        label=_("Supplier"), queryset=Supplier.objects.all(), required=False
    )
    estimated_arrival = forms.IntegerField()
    quantity = forms.IntegerField()

    def save(self, item: WebLinkOrderItem):
        obj = process_purchase_order(item=item, **self.cleaned_data)
        return obj

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('system_supplier') and not cleaned_data.get(
            'supplier'
        ):
            raise forms.ValidationError(
                _(
                    'Invalid value: One of the Supplier Fields should be provided'
                ),
                code='invalid',
            )


class PurchaseOrderItemRecieveForm(forms.Form):
    quantity = forms.IntegerField()

    def save(self, item: PurchaseOrderItem):
        if item.quantity < self.cleaned_data['quantity']:
            logger.debug(
                f"Exception raised due to heigher recieved quantity for {item.guid}"
            )
            raise forms.ValidationError(
                message=_("Quantity Recieved is more than ordered"),
                code="invalid",
            )
        obj = process_recieve_purchase_order_item(
            item=item, **self.cleaned_data
        )
        logger.debug(f"processing of {obj.guid} has been completed.")
        return obj
