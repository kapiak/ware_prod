import uuid
import logging

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.db.models import F, Sum
from django.db.models.functions import Coalesce

from wagtail.search import index

from assistant.core.models import BaseModel
from assistant.orders.models import Order, LineItem
from .exceptions import InsufficientStock

from .signals import stock_increased, allocated_stock

logger = logging.getLogger(__name__)


class Warehouse(index.Indexed, BaseModel):
    """A warehouse is a location where stock is available."""

    name = models.CharField(verbose_name=_("Name"), max_length=255)
    company_name = models.CharField(
        verbose_name=_("Company Name"), blank=True, max_length=255
    )
    email = models.EmailField(verbose_name=_("Email"), blank=True, default="")

    address = models.ForeignKey(
        "addresses.Address",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _("Warehouse")
        verbose_name_plural = _("Warehouses")

    def __str__(self):
        return f"{self.name}"

    search_fields = [
        index.SearchField("name"),
        index.SearchField("company_name"),
        index.SearchField("email"),
    ]


class StockQuerySet(models.QuerySet):
    def annotate_available_quantity(self):
        """The amount of available stock in the warehouse.
        Which is the available quantity - the allocated quantity.
        """
        return self.annotate(
            available_quantity=F("quantity")
            - Coalesce(Sum("allocations__quantity_allocated"), 0)
        )


class Stock(BaseModel):
    """Represents the amount of stock available in a particular warehouse.
    
    When stock is received from a supplier the quantity is increased.
    When stock is allocated to an order through the allocation model. the quantity is decreased. 
    """

    warehouse = models.ForeignKey(
        Warehouse, related_name="stocks", null=False, on_delete=models.CASCADE
    )
    product_variant = models.ForeignKey(
        "products.ProductVariant",
        null=False,
        on_delete=models.CASCADE,
        related_name="stocks",
    )
    quantity = models.PositiveIntegerField(default=0)

    objects = StockQuerySet.as_manager()

    def __str__(self):
        return f"{self.warehouse} - {self.product_variant.name} -> {self.quantity}"

    def increase_stock(self, quantity: int, commit: bool = True):
        """Incase given quantity of product variant to a stock in a warehouse."""
        self.quantity = F("quantity") + quantity
        if commit:
            self.save(update_fields=["quantity"])
            stock_increased.send(sender=self.__class__, instance=self, quantity=self.quantity, variant=self.product_variant)
            logger.info(f"Increasing stock by %s committed", quantity)

    def decrease_stock(self, quantity: int, commit: bool = True):
        """Incase given quantity of product variant to a stock in a warehouse."""
        self.quantity = F("quantity") - quantity
        if commit:
            self.save(update_fields=["quantity"])
            logger.info(f"Decreasing stock by %s committed", quantity)

    def allocate_to_order_line_item(self, line_item: uuid.UUID):
        """Allocate stock to an line item in and order if the stock is available
        in a specific warehouse.
        If there is not enough stock to allocate raise InsufficientStock
        """
        with transaction.atomic():
            if self.quantity >= line_item.unallocated_quantity:
                quantity = line_item.unallocated_quantity
                logger.info("Enough Stock to fully allocate to the line item.")
                Allocation.objects.create(
                    order_line=line_item,
                    stock=self,
                    quantity_allocated=quantity,
                )
                logger.info("Unallocated quantity is %s Current Quantity %s", quantity, self.quantity)
                self.decrease_stock(quantity, commit=True)
                allocated_stock.send(sender=self.__class__, instance=self, line_item=line_item)
                return True
            elif self.quantity < line_item.unallocated_quantity and self.quantity > 0:
                quantity = self.quantity
                logger.info("Not enough stock to fully allocate the line item. allocating what we can.")
                Allocation.objects.create(
                    order_line=line_item, stock=self, quantity_allocated=quantity,
                )
                logger.info("Unallocated quantity is %s Current Quantity %s", quantity, self.quantity)
                self.decrease_stock(quantity, commit=True)
                allocated_stock.send(sender=self.__class__, instance=self, line_item=line_item)
                return True
            else:
                raise InsufficientStock()

    class Meta:
        verbose_name = _("Stock")
        verbose_name = "Stock"


class Allocation(models.Model):
    order_line = models.ForeignKey(
        "orders.LineItem",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="allocations",
    )
    stock = models.ForeignKey(
        Stock,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="allocations",
    )
    quantity_allocated = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Allocation")
        verbose_name_plural = _("Allocations")

    def __str__(self):
        return f"{self.stock} allocated {self.quantity_allocated}"
