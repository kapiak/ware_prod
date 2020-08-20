from django import forms
from django.db import models

from assistant.orders.models import Order, LineItem
from assistant.products.models import ProductVariant
from assistant.purchases.models import PurchaseOrderItem
from assistant.warehouse.services import process_simple_stock_allocation
from .models import Warehouse, Stock


class AllocationForm(forms.Form):
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.all())
    stock = forms.UUIDField(widget=forms.HiddenInput())
    order_line = forms.UUIDField(widget=forms.HiddenInput())
    quantity = forms.IntegerField()

    def save(self):
        stock = Stock.objects.get(guid=self.cleaned_data["stock"])
        stock.allocate_to_order_line_item(
            line_item=LineItem.objects.get(guid=self.cleaned_data["order_line"]),
            quantity=self.cleaned_data["quantity"],
        )


class SimpleAllocationForm(forms.Form):
    def __init__(self, *args, **kwargs):

        variant = kwargs.pop("variant")
        super().__init__(*args, **kwargs)
        self.fields["orders"].queryset = LineItem.objects.filter(
            models.Q(variant=variant)
        ).exclude(
            models.Q(
                order__status__in=[
                    Order.StatusChoices.FULFILLED,
                    Order.StatusChoices.CANCELED,
                ]
            )
        )
        self.fields["variant"].queryset = ProductVariant.objects.filter(pk=variant.pk)

    variant = forms.ModelChoiceField(
        queryset=ProductVariant.objects.none(), widget=forms.HiddenInput()
    )
    orders = forms.ModelMultipleChoiceField(queryset=LineItem.objects.none())

    def save(self):
        items = process_simple_stock_allocation(**self.cleaned_data)
        return items


class StockReceiveForm(forms.Form):
    def __init__(self, *args, **kwargs):
        variant = kwargs.pop("variant")
        purchase_orders = kwargs.pop("purchase_orders")
        super().__init__(*args, **kwargs)
        self.fields["product_variant"].queryset = ProductVariant.objects.filter(
            pk=variant.pk
        )
        self.fields["purchase_orders"].queryset = purchase_orders

    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.all())
    product_variant = forms.ModelChoiceField(
        queryset=ProductVariant.objects.none(), widget=forms.HiddenInput()
    )
    purchase_orders = forms.ModelChoiceField(queryset=PurchaseOrderItem.objects.none())
    quantity = forms.IntegerField()
    attachment = forms.FileField()

