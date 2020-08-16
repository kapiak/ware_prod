from re import match

from django.db import models
from django.db.models import Max, Sum
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.search import index
from wagtail.core.models import Orderable
from django_measurement.models import MeasurementField
from measurement.measures import Weight

from assistant.core.models import BaseModel


class WeightUnits:
    KILOGRAM = "kg"
    POUND = "lb"
    OUNCE = "oz"
    GRAM = "g"

    CHOICES = [
        (KILOGRAM, "kg"),
        (POUND, "lb"),
        (OUNCE, "oz"),
        (GRAM, "g"),
    ]


def zero_weight():
    """Represent the zero weight value."""
    return Weight(kg=0)


class Order(index.Indexed, BaseModel, ClusterableModel):
    """The Orders model records all orders placed through the online store system
    by customers, as well as those created manually by administrators. 
    An order is created by syncing with an online e-commerce system.
    """

    class OrderType(models.TextChoices):
        REGULAR = "regular", _("Orders by customers")
        DRAFT = "draft", _("Created by staff, Not confirmed")

    class StatusChoices(models.TextChoices):
        # fully editable, not confirmed order created by staff users
        DRAFT = "draft", _("Draft")
        # order with no items marked as fulfilled
        UNFULFILLED = "unfulfilled", _("Unfulfilled")
        # order with some items marked as fulfilled
        PARTIALLY_FULFILLED = "partially fulfilled", _("Partially Fulfilled")
        # order with all items marked as fulfilled
        FULFILLED = "fulfilled", _("Fulfilled")
        # permanently canceled order
        CANCELED = "canceled", _("Canceled")

    class FinancialStatusChoices(models.TextChoices):
        # Show only authorized orders
        AUTHORIZED = "authorized", _("Authorized")
        # Show only pending orders
        PENDING = "pending", _("Pending")
        # Show only paid orders
        PAID = "paid", _("Paid")
        # Show only partially paid orders
        PARTIALLY_PAID = "partially_paid", _("Partially Paid")
        # Show only refunded orders
        REFUNDED = "refunded", _("Refunded")
        # Show only voided orders
        VOIDED = "voided", _("Voided")
        # Show only partially refunded orders
        PARTIALLY_REFUNDED = "partially_refunded", _("Partially Refunded")
        # Show orders of any financial status.
        ANY = "any", _("Any")
        # Show authorized and partially paid orders.
        UNPAID = "unpaid", _("Unpaid")

    class CancelReasonChoices(models.TextChoices):

        CUSTOMER = "customer", _("Customer")
        FRAUD = "fraud", _("Fraud")
        INVENTORY = "inventory", _("Inventory")
        DECLINED = "declined", _("Declined")
        OTHER = "other", _("Other")

    number = models.CharField(
        verbose_name=_("Order Number"),
        max_length=255,
        unique=True,
        help_text=_(
            "The order 's position in the shop's count of orders starting at 1001. "
            "Order numbers are sequential and start at 1001."
        ),
    )
    customer_email = models.EmailField(blank=True, default="")
    customer_id = models.CharField(max_length=255, blank=True, null=True)

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_(
            "The sum of all line item prices, discounts, shipping, taxes, and tips in the shop currency. "
            "Must be positive."
        ),
    )
    subtotal_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        help_text=_(
            "The price of the order in the shop currency after discounts but before shipping, taxes, and tips."
        ),
    )
    total_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        help_text=_(
            "The sum of all the taxes applied to the order in th shop currency. Must be positive."
        ),
    )

    weight = MeasurementField(
        measurement=Weight,
        unit_choices=WeightUnits.CHOICES,
        default=zero_weight,
    )

    status = models.CharField(
        max_length=32,
        default=StatusChoices.UNFULFILLED,
        choices=StatusChoices.choices,
    )
    financial_status = models.CharField(
        verbose_name=_("Financial Status"),
        max_length=100,
        default=FinancialStatusChoices.UNPAID,
        choices=FinancialStatusChoices.choices,
    )
    type = models.CharField(
        max_length=32, default=OrderType.REGULAR, choices=OrderType.choices,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="orders",
        on_delete=models.SET_NULL,
    )

    billing_address = models.ForeignKey(
        "addresses.Address",
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
    )
    shipping_address = models.ForeignKey(
        "addresses.Address",
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
    )

    cancel_reason = models.CharField(
        verbose_name=_("Cancel Reason"),
        max_length=100,
        choices=CancelReasonChoices.choices,
        blank=True,
        help_text=_("The reason why the order was canceled."),
    )
    cancelled_at = models.DateTimeField(
        verbose_name=_("Canceled at"),
        blank=True,
        null=True,
        help_text=_("The date and time when the order was canceled."),
    )
    closed_at = models.DateTimeField(
        verbose_name=_("Closed at"),
        blank=True,
        null=True,
        help_text=_("The date and time when the order was closed."),
    )

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def save(self, **kwargs):
        if self.cancel_reason:
            # Deallocated the stock
            pass


class LineItem(index.Indexed, Orderable, BaseModel):
    """ """

    order = ParentalKey(Order, related_name="lines", on_delete=models.CASCADE)
    variant = models.ForeignKey(
        "products.ProductVariant",
        related_name="order_lines",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    is_shipping_required = models.BooleanField()
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    quantity_fulfilled = models.IntegerField(
        validators=[MinValueValidator(0)], default=0
    )

    @property
    def quantity_unfulfilled(self):
        return self.quantity - self.quantity_fulfilled

    @property
    def allocated(self):
        return self.allocations.aggregate(allocated=Sum("quantity_allocated"))

    @property
    def requires(self):
        return self.quantity - self.allocated['allocated']

    def __str__(self):
        return f"#{self.order.number} - {self.variant.sku} -> {self.quantity_unfulfilled}"


# class Fulfillment(index.Indexed, BaseModel):
#     """The fulfillment represents a group of shipped items with a corresponding
#     tracking number. Fulfillments are created by a shop operator and usually
#     represent physical shipments.

#     Fulfillment means whether an order has been sent to the customer or not
#     """

#     class FulfillmentStatus(models.TextChoices):
#         # group of products in an order marked as fulfilled
#         ULFILLED = "fulfilled", _("Fulfilled")
#         # fulfilled group of products in an order marked as canceled
#         CANCELED = "canceled", _("Canceled")

#     fulfillment_order = models.PositiveIntegerField(editable=False)
#     order = models.ForeignKey(
#         Order,
#         related_name="fulfillments",
#         editable=False,
#         on_delete=models.CASCADE,
#     )
#     status = models.CharField(
#         max_length=32,
#         default=FulfillmentStatus.FULFILLED,
#         choices=FulfillmentStatus.choices,
#     )
#     tracking_number = models.CharField(max_length=255, default="", blank=True)
#     created = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("Fullfullment")
#         verbose_name_plural = _("Fullfilments")

#     def __str__(self):
#         return f"Fulfillment #{self.composed_id}"

#     def __iter__(self):
#         return iter(self.lines.all())

#     def save(self, *args, **kwargs):
#         """Assign an auto incremented value as a fulfillment order."""
#         if not self.pk:
#             groups = self.order.fulfillments.all()
#             existing_max = groups.aggregate(Max("fulfillment_order"))
#             existing_max = existing_max.get("fulfillment_order__max")
#             self.fulfillment_order = (
#                 existing_max + 1 if existing_max is not None else 1
#             )
#         return super().save(*args, **kwargs)

#     @property
#     def composed_id(self):
#         return "%s-%s" % (self.order.id, self.fulfillment_order)

#     def can_edit(self):
#         return self.status != self.FulfillmentStatus.CANCELED

#     def get_total_quantity(self):
#         return sum([line.quantity for line in self])

#     @property
#     def is_tracking_number_url(self):
#         return bool(match(r"^[-\w]+://", self.tracking_number))


# class FulfillmentLine(Orderable):
#     order_line = models.ForeignKey(
#         LineItem, related_name="+", on_delete=models.CASCADE
#     )
#     fulfillment = models.ForeignKey(
#         Fulfillment, related_name="lines", on_delete=models.CASCADE
#     )
#     quantity = models.PositiveIntegerField()
#     stock = models.ForeignKey(
#         "warehouse.Stock",
#         related_name="fulfillment_lines",
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#     )
