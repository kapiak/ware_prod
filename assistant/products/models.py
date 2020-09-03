from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_measurement.models import MeasurementField
from djmoney.models.fields import MoneyField
from measurement.measures import Weight
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable
from wagtail.search import index

from assistant.core.models import BaseModel
from assistant.purchases.models import PurchaseOrderItem


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


class Vendor(index.Indexed, BaseModel):
    """Represents a vendor or a supplier for a product"""

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        help_text=_("Required, Maximum of 255 Characters"),
    )

    class Meta:
        verbose_name = _("Vendor")
        verbose_name_plural = _("Vendors")

    def __str__(self) -> str:
        return f"{self.name}"

    @property
    def total_products(self) -> int:
        return self.products.count()


class Supplier(index.Indexed, BaseModel):
    """Represents a supplier of a product variant."""

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        help_text=_("Required, Maximum of 255 Characters"),
    )

    website = models.URLField(max_length=256, blank=True, null=True)

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")

    def __str__(self) -> str:
        return self.name


class ProductType(index.Indexed, BaseModel):
    """Think about product types as templates for your products. Multiple products can use the same product type."""

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        help_text=_("Required, Maximum of 255 characters."),
    )
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    weight = MeasurementField(
        measurement=Weight, unit_choices=WeightUnits.CHOICES, blank=True, null=True,
    )

    class Meta:
        verbose_name = _("Product Type")
        verbose_name_plural = _("Products Types")

    def __str__(self) -> str:
        return f"{self.name}"


class Product(index.Indexed, BaseModel, ClusterableModel):
    """The product concept reflects the common details of several product variants.
    
    If the product variant has no overridden property 
    (for example: price specifically set for this variant), 
    the default value is taken from the product.
    """

    product_type = models.ForeignKey(
        ProductType, related_name="products", on_delete=models.SET_NULL, null=True,
    )

    title = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = RichTextField(blank=True, null=True)
    weight = MeasurementField(
        measurement=Weight, unit_choices=WeightUnits.CHOICES, blank=True, null=True,
    )

    max_price = MoneyField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default_currency=settings.DEFAULT_CURRENCY,
    )
    min_price = MoneyField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default_currency=settings.DEFAULT_CURRENCY,
    )

    vendor = models.ForeignKey(
        Vendor, related_name="products", on_delete=models.CASCADE, null=True
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self) -> str:
        return f"{self.title}"

    def get_first_image(self):
        images = list(self.images.all())
        return images[0] if images else None

    search_fields = [
        index.SearchField("title"),
        index.SearchField("product_type"),
        index.SearchField("description"),
        index.FilterField("vendor"),
        index.FilterField("created_at"),
    ]


class ProductVariant(index.Indexed, Orderable, BaseModel):
    """Variants are the most important objects. All operations on stock utilize variants. 
    
    Each product variant has also a stock-keeping unit (SKU).

    Each variant holds information about:

    - Quantity at hand
    - Quantity allocated for already placed orders
    - Quantity available

    Each variant also has a cost price (the price that your store had to pay to purchase it).

    Within a variant, stock information is split between warehouses.
    the Inventory card to define which warehouses carry that particular SKU 
    and what quantities they hold.

    * A variant is in stock, if it has unallocated quantity.
    """

    product = ParentalKey(Product, related_name="variants", on_delete=models.CASCADE)

    sku = models.CharField(
        verbose_name=_("SKU (Stock Keeping Unit)"), max_length=255, unique=True
    )
    barcode = models.CharField(verbose_name=_("Barcode"), max_length=255, unique=True)
    name = models.CharField(verbose_name=_("Name"), max_length=255, blank=True)
    price = MoneyField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default_currency=settings.DEFAULT_CURRENCY,
    )
    cost_price = MoneyField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default_currency=settings.DEFAULT_CURRENCY,
        null=True,
        blank=True,
    )
    weight = MeasurementField(
        measurement=Weight, unit_choices=WeightUnits.CHOICES, blank=True, null=True,
    )
    metadata = models.JSONField(default=dict, blank=True)

    images = models.ManyToManyField("ProductImage", through="VariantImage")

    class Meta:
        verbose_name = _("Product Variant")
        verbose_name_plural = _("Products Variants")

    def __str__(self) -> str:
        return self.name or self.sku

    def get_weight(self) -> "Weight":
        return self.weight or self.product.weight or self.product.product_type.weight

    def get_first_image(self) -> "ProductImage":
        images = list(self.images.all())
        return images[0] if images else self.product.get_first_image()

    @property
    def available_stock(self):
        val = self.stocks.aggregate(quantity=models.Sum("quantity"))["quantity"]
        return val or 0

    @property
    def allocated(self):
        return (
            self.stocks.aggregate(
                quantity=models.Sum("allocations__quantity_allocated")
            )["quantity"]
            or 0
        )

    @property
    def needed_stock(self):
        from assistant.orders.models import Order

        val = self.order_lines.exclude(
            order__status__in=[
                Order.StatusChoices.FULFILLED,
                Order.StatusChoices.CANCELED,
            ]
        ).aggregate(quantity=models.Sum("quantity"))['quantity']
        return val or 0

    @property
    def in_purchase(self):
        return PurchaseOrderItem.objects.filter(variant=self).aggregate(quantity=models.Sum("quantity"))["quantity"] or 0

class ProductImage(Orderable, BaseModel):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    alt = models.CharField(verbose_name=_("Image Alt Text"), max_length=128, blank=True)

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Products Images")

    def get_ordering_queryset(self) -> "models.QuerySet":
        return self.product.images.all()


class VariantImage(models.Model):
    variant = models.ForeignKey(
        "ProductVariant", related_name="variant_images", on_delete=models.CASCADE,
    )
    image = models.ForeignKey(
        ProductImage, related_name="variant_images", on_delete=models.CASCADE
    )
