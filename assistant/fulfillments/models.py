from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.search import index
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from assistant.core.models import BaseModel
from assistant.orders.models import Order

logger = logging.getLogger(__name__)


class Fulfillment(index.Indexed, BaseModel, ClusterableModel):
    fulfillment_order = models.PositiveIntegerField(editable=False)
    order = models.ForeignKey(
        Order, related_name="fulfillments", editable=False, on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=32,
        default=FulfillmentStatus.FULFILLED,
        choices=FulfillmentStatus.CHOICES,
    )
    tracking_number = models.CharField(max_length=255, default="", blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Fulfillment")
        verbose_name_plural = _("Fulfillments")

    def __str__(self):
        return f"Fulfillment #{self.composed_id}"

    def __iter__(self):
        return iter(self.lines.all())

    def save(self, *args, **kwargs):
        """Assign an auto incremented value as a fulfillment order."""
        if not self.pk:
            groups = self.order.fulfillments.all()
            existing_max = groups.aggregate(Max("fulfillment_order"))
            existing_max = existing_max.get("fulfillment_order__max")
            self.fulfillment_order = existing_max + 1 if existing_max is not None else 1
        return super().save(*args, **kwargs)

    @property
    def composed_id(self):
        return "%s-%s" % (self.order.id, self.fulfillment_order)

    def can_edit(self):
        return self.status != FulfillmentStatus.CANCELED

    def get_total_quantity(self):
        return sum([line.quantity for line in self])

    @property
    def is_tracking_number_url(self):
        return bool(match(r"^[-\w]+://", self.tracking_number))


class FulfillmentLine(models.Model):
    order_line = models.ForeignKey(
        OrderLine, related_name="+", on_delete=models.CASCADE
    )
    fulfillment = ParentalKey(
        Fulfillment, related_name="lines", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    stock = models.ForeignKey(
        "warehouse.Stock",
        related_name="fulfillment_lines",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
