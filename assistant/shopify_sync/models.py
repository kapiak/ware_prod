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