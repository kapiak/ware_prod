from sequences import get_next_value

from assistant.products.models import Supplier, ProductVariant
from .models import PurchaseOrder, PurchaseOrderItem


def process_purchase_order(**data) -> PurchaseOrder:
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
    purchase_order_item = PurchaseOrderItem.objects.create(
        purchase_order=obj,
        quantity=data.get("quantity"),
        status=PurchaseOrder.StatusChoices.DRAFT,
    )
    for sales_order in data.get("sales_orders"):
        sales_order.purchase_order = purchase_order_item
        sales_order.save()
    return obj


def process_add_to_purchase_order(item, **kwargs):
    pass
