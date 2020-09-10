from django import forms
from django.contrib.auth import get_user_model
from django.forms import formset_factory

from .models import ShipmentLine, ShipmentPiece, ShippingMethod
from assistant.orders.models import LineItem

User = get_user_model()

class ShipmentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order')
        super().__init__(*args, **kwargs)

    shipping_method = forms.ModelChoiceField(queryset=ShippingMethod.objects.all())
    shipper = forms.ModelChoiceField(queryset=User.objects.all())


class ShipmentLineDetailForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop('item')
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = ShipmentLine.objects.filter(guid=self.item.guid)
    
    item = forms.ModelChoiceField(queryset=ShipmentLine.objects.all(), widget=forms.HiddenInput())
    weight = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    width = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    height = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    depth = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    declared_value = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def save(self):
        order_line_item = LineItem.objects.get(guid=self.item.order_line.guid)
        variant = order_line_item.variant
        variant.weight = self.cleaned_data["weight"]
        variant.width = self.cleaned_data["width"]
        variant.height = self.cleaned_data["height"]
        variant.depth = self.cleaned_data["depth"]
        variant.declared_value = self.cleaned_data["depth"]
        variant.save()


class PieceForm(forms.Form):
    pass
