from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import Country, CountryField
from django_measurement.models import MeasurementField
from djmoney.models.fields import MoneyField
from measurement.measures import Weight
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.search import index

from assistant.core.models import BaseModel
from assistant.orders.models import LineItem, Order


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


class ShippingZone(BaseModel):
    name = models.CharField(max_length=100)
    countries = CountryField(multiple=True, default=[], blank=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def price_range(self):
        prices = [
            shipping_method.get_total()
            for shipping_method in self.shipping_methods.all()
        ]
        return prices


class ShippingMethod(BaseModel):

    class ShippingMethodType(models.TextChoices):
        PRICE_BASED = "price", _("Price")
        WEIGHT_BASED = "weight", _("Weight")

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=30, choices=ShippingMethodType.choices)
    price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    shipping_zone = models.ForeignKey(
        ShippingZone, related_name="shipping_methods", on_delete=models.CASCADE
    )
    minimum_order_price = MoneyField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default_currency=settings.DEFAULT_CURRENCY,
    )
    maximum_order_price = MoneyField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default_currency=settings.DEFAULT_CURRENCY,
    )

    minimum_order_weight = MeasurementField(
        measurement=Weight,
        unit_choices=WeightUnits.CHOICES,
        default=0,
    )
    maximum_order_weight = MeasurementField(
        measurement=Weight, unit_choices=WeightUnits.CHOICES, blank=True, null=True
    )

    meta = models.JSONField(blank=True, default=dict)

    class Meta:
        verbose_name = _("Shipping Method")
        verbose_name_plural = _("Shipping Methods")

    def __str__(self):
        return self.name

    def get_total(self):
        return self.price_amount


class Shipment(index.Indexed, BaseModel, ClusterableModel):
    """A fulfillment is record which represents the fulfillment of a set of order lines.
    
    TODO: Add combined shipments if the Shipping Address is Similar.
    """

    number = models.CharField(
        verbose_name=_("Order Number"),
        max_length=255,
        unique=True,
        help_text=_(
            "The shipment's number are sequential and start at 1001."
        ),
    )
    shipping_method = models.ForeignKey(ShippingMethod, related_name="shipments", on_delete=models.SET_NULL, null=True)
    shipper = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="shipments", on_delete=models.SET_NULL, null=True)

    order = models.ForeignKey("orders.Order", related_name="shipments", on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Shipment")
        verbose_name_plural = _("Shipments")

    def __str__(self):
        return f"{self.number}"


class ShipmentLine(BaseModel):
    """Represents a line in the shipment or an export declaration"""

    shipment = ParentalKey(Shipment, related_name="lines", on_delete=models.CASCADE)
    order_line = models.ForeignKey("orders.LineItem", related_name="shipment_line", on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Shipment Line")
        verbose_name_plural = _("Shipments Lines")

    def __str__(self):
        return f"{self.shipment.number} - {self.order_line}"


class ShipmentPiece(BaseModel):
    """Represents the physical shipped item as box or envelope etc..."""

    shipment = ParentalKey(Shipment, related_name="pieces", on_delete=models.CASCADE)
    weight = MeasurementField(
        measurement=Weight, unit_choices=WeightUnits.CHOICES, default=0,
    )
    height = models.DecimalField(verbose_name=_("Height"), max_digits=20, decimal_places=4, null=True, blank=True)
    depth = models.DecimalField(verbose_name=_("Depth"), max_digits=20, decimal_places=4, null=True, blank=True)
    width = models.DecimalField(verbose_name=_("Width"), max_digits=20, decimal_places=4, null=True, blank=True)
    declared_value = models.DecimalField(verbose_name=_("Declared Value"), max_digits=20, decimal_places=4, null=True, blank=True)

    class Meta:
        verbose_name = _("Shipment Piece")
        verbose_name_plural = _("Shipments Pieces")

    def __str__(self):
        return f"{self.order.number}"