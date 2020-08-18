from django.db import models
from django.conf import settings

from django.utils.translation import gettext_lazy as _

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.search import index
from wagtail.core.models import Orderable
from djmoney.models.fields import MoneyField
from measurement.measures import Weight
from django_measurement.models import MeasurementField

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


class WebLinkOrder(index.Indexed, BaseModel, ClusterableModel):
    """The order represents the request by a customer to purchase a set of
    items
    """

    class StatusChoices(models.TextChoices):
        NEW = 'new', _("New")
        INIT = 'init', _("Puchase Order Made")
        SUBMITTED = 'submitted', _("Submitted Purchase Order")
        STOCK_RECIEVED = 'stock-recieved', _("Stock Recieved")
        SENT = 'sent', _("Stock Sent to Customer")
        CANCELED = 'cancelled', _("Order Cancelled")

    number = models.CharField(
        verbose_name=_("Number"),
        max_length=100,
        help_text=_("Auto Generated order number"),
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=100,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="weblink_orders",
        on_delete=models.SET_NULL,
        null=True,
    )
    address = models.ForeignKey(
        "addresses.Address",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
    )
    shipping_method = models.CharField(
        verbose_name=_("Shipping Method"), max_length=255, null=True
    )
    weight = MeasurementField(
        measurement=Weight,
        unit_choices=WeightUnits.CHOICES,
        blank=True,
        null=True,
    )  # TODO: move to a relation with the shipping method model

    class Meta:
        verbose_name = _("Web Link Order")
        verbose_name_plural = _("Web Link Orders")

    def __str__(self):
        return f"{self.number}"


class WebLinkOrderItem(index.Indexed, Orderable, BaseModel):
    """An item in the Weblink order"""

    class StatusChoices(models.TextChoices):
        NEW = 'new', _("New")
        INIT = 'init', _("Puchase Order Made")
        SUBMITTED = 'submitted', _("Submitted Purchase Order")
        STOCK_RECIEVED = 'stock-recieved', _("Stock Recieved")
        SENT = 'sent', _("Stock Sent to Customer")
        CANCELED = 'cancelled', _("Order Cancelled")

    order = ParentalKey(
        WebLinkOrder, related_name="items", on_delete=models.CASCADE
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=100,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
    )
    url = models.TextField(verbose_name=_("The product URL"))
    name = models.CharField(verbose_name=_("The Product Name"), max_length=255)
    provided_price = MoneyField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default_currency=settings.DEFAULT_CURRENCY,
    )
    quantity = models.PositiveIntegerField()
    weight = MeasurementField(
        measurement=Weight,
        unit_choices=WeightUnits.CHOICES,
        blank=True,
        null=True,
    )
    comments = models.TextField(verbose_name=_("Comments"), blank=True)

    class Meta:
        verbose_name = _("Web Link Order Item")
        verbose_name_plural = _("Web Link Orders Items")

    def __str__(self):
        return f"{self.name}"


class PurchaseOrder(index.Indexed, BaseModel, ClusterableModel):
    """Represents the order made to the product supplier to pruchase the item."""

    class StatusChoices(models.TextChoices):
        DRAFT = 'draft', _("Draft")
        SENT = 'sent', _("Sent")
        RECIEVED = 'recieved', _("Recieved")

    sales_order = models.ForeignKey(
        WebLinkOrder, related_name="purchase_orders", on_delete=models.PROTECT
    )
    number = models.CharField(verbose_name=_("Number"), max_length=100)
    estimated_arrival = models.IntegerField(
        verbose_name=_("Estimated Arrival in Days")
    )
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

    purchase_order = ParentalKey(
        PurchaseOrder, related_name="items", on_delete=models.CASCADE
    )
    sales_order_item = models.OneToOneField(
        WebLinkOrderItem,
        related_name="puchase_order_item",
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = _("Purchase Order Item")
        verbose_name_plural = _("Pruchase Order Items")
