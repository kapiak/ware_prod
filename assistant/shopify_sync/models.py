from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField

from assistant.core.models import BaseModel


class ShopifySyncLog(BaseModel):
    """Ever time a syc operation is done a log is kept here"""

    class SyncStatus(models.TextChoices):
        STARTED = 'started', _("Started")
        SUCCEEDED = 'succeeded', _("Succeeded")
        FAILED = 'failed', _("Failed")

    status_code = models.IntegerField(
        verbose_name=_("Status Code"), null=True, blank=True
    )
    response_data = JSONField(blank=True, default=dict)
    status = models.CharField(
        verbose_name=_("Status"), max_length=255, choices=SyncStatus.choices
    )

    class Meta:
        verbose_name = _("Shopify Sync Log")
        verbose_name_plural = _("Shopify Sync Logs")
