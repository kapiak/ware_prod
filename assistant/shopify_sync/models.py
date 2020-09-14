from django.db import models
from django.utils.translation import gettext_lazy as _

from assistant.core.models import BaseModel


class ShopifySyncLog(BaseModel):
    """Ever time a syc operation is done a log is kept here"""

    class SyncStatus(models.TextChoices):
        STARTED = 'started', _("Started")
        SUCCEEDED = 'succeeded', _("Succeeded")
        FAILED = 'failed', _("Failed")

    class ObjectTypeChoices(models.TextChoices):
        PRODUCT = 'product', _('Product')
        ORDER = 'order', _('Order')
        FULFILLMENT = 'fulfillment', _("Fulfillment")

    status_code = models.IntegerField(
        verbose_name=_("Status Code"), null=True, blank=True
    )
    object_type = models.CharField(verbose_name=_("Object Type"), max_length=100, choices=ObjectTypeChoices.choices, blank=True)
    data = models.JSONField(blank=True, default=dict)
    metadata = models.JSONField(blank=True, default=dict)
    status = models.CharField(
        verbose_name=_("Status"), max_length=255, choices=SyncStatus.choices
    )

    class Meta:
        verbose_name = _("Shopify Sync Log")
        verbose_name_plural = _("Shopify Sync Logs")


class ErrorSyncLog(BaseModel):
    """Sync Error Log"""

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Error Sync Log")
        verbose_name_plural = _("Errors Sync Log")



class EventStore(BaseModel):
    """An event store which stores all the events coming in from the shopify webhooks"""

    class StatusChoices(models.TextChoices):
        RECEIVED = 'received', _("Received")
        IN_PROCESS = 'in-process', _("In Process")
        SUCCESS = 'success', _("Success")
        FAILED = 'failed', _("Failed")

    domain = models.CharField(verbose_name=_("Domain"), max_length=100, blank=True)
    topic = models.CharField(verbose_name=_("Topic"), max_length=100, blank=True)
    data = models.JSONField(blank=True, default=dict)

    status = models.CharField(_("Status"), max_length=50, choices=StatusChoices.choices, default=StatusChoices.RECEIVED)
    error_data = models.JSONField(verbose_name=_("Error Data"), default=dict, blank=True)

    class Meta:
        verbose_name = _("Event Store")
        verbose_name_plural = _("Events Store")

    def __str__(self):
        return f"{self.domain} - {self.topic}"

    @property
    def topic_icon(self):
        icon_mapper = {
            'app/uninstalled': "fas fa-clock bg-blue",
            'carts/create': "fas fa-shopping-cart bg-blue",
            'carts/update': "fas fa-shopping-cart bg-green",
            'checkouts/create': "fas fa-clock bg-blue",
            'checkouts/update': "fas fa-clock bg-blue",
            'checkouts/delete': "fas fa-clock bg-red",
            'collections/create': "fas fa-clock bg-blue",
            'collections/update': "fas fa-clock bg-green",
            'collections/delete': "fas fa-clock bg-red",
            'customer_groups/create': "fas fa-user bg-blue",
            'customer_groups/update': "fas fa-user bg-green",
            'customer_groups/delete': "fas fa-user bg-red",
            'customers/create': "fas fa-user bg-blue",
            'customers/disable': "fas fa-user bg-yellow",
            'customers/delete': "fas fa-user bg-red",
            'customers/enable': "fas fa-user bg-green",
            'customers/update': "fas fa-user bg-green",
            'disputes/create': "fas fa-clock bg-blue",
            'disputes/update': "fas fa-clock bg-green",
            'fulfillments/create': "fas fa-truck-moving bg-blue",
            'fulfillments/update': "fas fa-truck-moving bg-green",
            'orders/create': "fas fa-shopping-basket bg-blue",
            'orders/delete': "fas fa-shopping-basket bg-red",
            'orders/updated': "fas fa-shopping-basket bg-green",
            'orders/paid': "fas fa-shopping-basket bg-green",
            'orders/cancelled': "fas fa-shopping-basket bg-red",
            'orders/fulfilled': "fas fa-shopping-basket bg-green",
            'orders/partially_fulfilled': "fas fa-shopping-basket bg-green",
            'order_transactions/create': "fas fa-shopping-basket bg-blue",
            'products/create': "fas fa-boxes bg-blue",
            'products/update': "fas fa-boxes bg-green",
            'products/delete': "fas fa-boxes bg-red",
            'refunds/create': "fas fa-clock bg-blue",
            'shop/update': "fas fa-clock bg-green",
            'draft_orders_create': "fas fa-clock bg-blue",
            'draft_orders_update': "fas fa-clock bg-green"
        }
        icon = icon_mapper.get(self.topic)
        return icon
        