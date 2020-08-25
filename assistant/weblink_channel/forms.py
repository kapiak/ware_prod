from django import forms
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


class CustomerInformationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "form.customer_form.email",
            }
        )
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "form.customer_form.name",
            }
        )
    )
    country = CountryField().formfield(
        initial="MY",
        widget=forms.Select(
            attrs={
                "class": "block appearance-none w-full bg-white border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500",
                "v-model": "form.customer_form.country",
            }
        ),
    )
    state = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "form.customer_form.state",
            }
        )
    )
    city = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "form.customer_form.city",
            }
        )
    )
    code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "form.customer_form.code",
            }
        )
    )


class ShippingInformationForm(forms.Form):
    method = forms.ChoiceField(
        initial="skynet",
        choices=[("skynet", _("Skeynet")), ("ems", _("EMS"))],
        widget=forms.Select(
            attrs={
                "class": "block appearance-none w-full bg-white border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500",
                "v-model": "form.shipping_form.method",
            }
        ),
    )
    weight = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg py-2 px-4 block w-full appearance-none leading-normal",
                "v-model": "form.shipping_form.weight",
            }
        )
    )


class ProductAddForm(forms.Form):
    url = forms.URLField(
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
    price = forms.DecimalField(
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
