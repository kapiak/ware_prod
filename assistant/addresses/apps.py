from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AddressesConfig(AppConfig):
    name = 'assistant.addresses'
    verbose_name = _("Addresses")
