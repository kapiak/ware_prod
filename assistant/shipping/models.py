from django.db import models

from django_countries.fields import Country, CountryField

from assistant.core.models import BaseModel


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


class ShippingMethod(models.Model):

    class ShippingMethodType(models.TextChoices):
        PRICE_BASED = "price", _("Price")
        WEIGHT_BASED = "weight", _("Weight")

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=30, choices=ShippingMethodType.CHOICES)
    price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    shipping_zone = models.ForeignKey(
        ShippingZone, related_name="shipping_methods", on_delete=models.CASCADE
    )
    minimum_order_price = MoneyField(
        amount_field="minimum_order_price_amount", currency_field="currency"
    )
    maximum_order_price = MoneyField(
        amount_field="maximum_order_price_amount", currency_field="currency"
    )

    minimum_order_weight = MeasurementField(
        measurement=Weight,
        unit_choices=WeightUnits.CHOICES,
        default=zero_weight,
        blank=True,
        null=True,
    )
    maximum_order_weight = MeasurementField(
        measurement=Weight, unit_choices=WeightUnits.CHOICES, blank=True, null=True
    )

    meta = JSONField(blank=True, default=dict, encoder=CustomJsonEncoder)

    objects = ShippingMethodQueryset.as_manager()
    translated = TranslationProxy()

    class Meta:
        verbose_name = _("Shipping Method")
        verbose_name_plural = _("Shipping Methods")

    def __str__(self):
        return self.name

    def __repr__(self):
        if self.type == ShippingMethodType.PRICE_BASED:
            minimum = "%s%s" % (
                self.minimum_order_price.amount,
                self.minimum_order_price.currency,
            )
            max_price = self.maximum_order_price
            maximum = (
                "%s%s" % (max_price.amount, max_price.currency)
                if max_price
                else "no limit"
            )
            return "ShippingMethod(type=%s min=%s, max=%s)" % (
                self.type,
                minimum,
                maximum,
            )
        return "ShippingMethod(type=%s weight_range=(%s)" % (
            self.type,
            _get_weight_type_display(
                self.minimum_order_weight, self.maximum_order_weight
            ),
        )

    def get_total(self):
        return self.price