from django import forms

from assistant.orders.models import LineItem
from .models import Warehouse, Stock


class AllocationForm(forms.Form):
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.all())
    stock = forms.UUIDField(widget=forms.HiddenInput())
    order_line = forms.UUIDField(widget=forms.HiddenInput())
    quantity = forms.IntegerField()

    def save(self):
        stock = Stock.objects.get(guid=self.cleaned_data['stock'])
        stock.allocate_to_order_line_item(
            line_item=LineItem.objects.get(
                guid=self.cleaned_data['order_line']
            ),
            quantity=self.cleaned_data['quantity'],
        )
