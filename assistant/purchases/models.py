from django.db import models
from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

from django.utils.translation import gettext_lazy as _

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.search import index
from wagtail.core.models import Orderable
from djmoney.models.fields import MoneyField
from measurement.measures import Weight
from django_measurement.models import MeasurementField

from assistant.core.models import BaseModel


class PurchaseOrder(index.Indexed, BaseModel, ClusterableModel):
    """Represents the order made to the product supplier to purchase the item."""

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SUBMITTED = "submitted", _("Submitted")
        RECEIVED = "received", _("Received")
        PARTIAL = "partial", _("Partially Received")

    number = models.CharField(verbose_name=_("Number"), max_length=100)
    estimated_arrival = models.IntegerField(verbose_name=_("Estimated Arrival in Days"))
    supplier = models.ForeignKey(
        "products.Supplier",
        related_name="purchase_orders",
        on_delete=models.SET_NULL,
        null=True,
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=100,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )

    class Meta:
        verbose_name = _("Purchase Order")
        verbose_name_plural = _("Purchase Orders")

    def __str__(self):
        return f"{self.number}"


class PurchaseOrderItem(index.Indexed, Orderable, BaseModel):
    """Represents an item in the purchase order"""

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SUBMITTED = "submitted", _("Submitted")
        RECEIVED = "received", _("Received")
        PARTIAL = "partial", _("Partially Received")

    purchase_order = ParentalKey(
        PurchaseOrder, related_name="items", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=100,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )
    received = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Purchase Order Item")
        verbose_name_plural = _("Purchase Order Items")

    def __str__(self):
        return f"#{self.purchase_order.number} | {self.quantity}"
