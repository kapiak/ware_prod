from sequences import get_next_value

from assistant.products.models import Supplier, ProductVariant
from .models import PurchaseOrder, PurchaseOrderItem


def process_add_to_purchase_order(
    variant, purchase_order, **data
) -> PurchaseOrder:
    PurchaseOrderItem.objects.create(
        purchase_order=purchase_order,
        variant=variant,
        quantity=data.get("quantity"),
        status=PurchaseOrder.StatusChoices.DRAFT,
    )
    return purchase_order


def process_purchase_order(variant, **data) -> PurchaseOrder:
    system_supplier = data.get("system_supplier", None)
    if system_supplier:
        supplier = data["system_supplier"]
    else:
        supplier = Supplier.objects.create(name=data["supplier"])
    obj = PurchaseOrder.objects.create(
        number=get_next_value("purchase_order_number", initial_value=1000),
        estimated_arrival=data["estimated_arrival"],
        supplier=supplier,
    )
    PurchaseOrderItem.objects.create(
        purchase_order=obj,
        variant=variant,
        quantity=data.get("quantity"),
        status=PurchaseOrder.StatusChoices.DRAFT,
    )
    return obj
