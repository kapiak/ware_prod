from django import forms
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


class CustomerInformationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "cart.customer.email",
            }
        )
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "cart.customer.name",
            }
        )
    )
    country = CountryField().formfield(
        widget=forms.Select(
            attrs={
                "class": "block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500",
                "v-model": "cart.customer.country",
            }
        )
    )
    state = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "cart.customer.state",
            }
        )
    )
    city = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "cart.customer.city",
            }
        )
    )
    postal_code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "cart.customer.code",
            }
        )
    )


class ShippingInformationForm(forms.Form):
    shipping_method = forms.ChoiceField(
        choices=[("DHL", _("DHL")), ("FEDEX", _("FedEx")), ("USPS", _("USPS"))],
        widget=forms.Select(
            attrs={
                "class": "block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500",
                "v-model": "cart.shipping.method",
            }
        ),
    )
    total_weight = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "cart.shipping.weight",
            }
        )
    )


class ProductAddForm(forms.Form):
    link = forms.URLField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "item.url",
            }
        )
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "item.name",
            }
        )
    )
    quantity = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "item.quantity",
            }
        )
    )
    unite_price = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "item.price",
            }
        )
    )
    comments = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "item.comments",
            }
        )
    )
