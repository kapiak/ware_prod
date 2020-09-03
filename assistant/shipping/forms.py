from django import forms
from django.contrib.auth import get_user_model
from django.forms import formset_factory

from .models import ShipmentLine, ShipmentPiece, ShippingMethod

User = get_user_model()

class ShipmentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order')
        super().__init__(*args, **kwargs)

    shipping_method = forms.ModelChoiceField(queryset=ShippingMethod.objects.all())
    shipper = forms.ModelChoiceField(queryset=User.objects.all())


class ShipmentLineForm(forms.Form):
    pass


class PieceForm(forms.Form):
    pass
