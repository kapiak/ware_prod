import logging
import uuid

from django.contrib.auth import get_user_model
from sequences import get_next_value

from assistant.orders.models import LineItem
from assistant.shipping.models import Shipment, ShipmentLine, ShipmentPiece
from config import celery_app

from .services import allocate_stock

logger = logging.getLogger(__name__)


@celery_app.task()
def allocate_stock_task(guid: uuid.UUID):
    """A Celery task to allocate stock to sales orders."""
    allocate_stock(guid)


@celery_app.task()
def create_shipment_task(guid: uuid.UUID):
    """A Celery task to create order shipment."""
    line_item = LineItem.objects.get(guid=guid)

    try:
        shipment = Shipment.objects.get(order=line_item.order)
    except Shipment.DoesNotExist as de:
        logger.info("No shipment has been made for this order yet. %s", de)
        shipment = Shipment.objects.create(
            number=get_next_value('shipment_number', initial_value=1000),
            order=line_item.order
        )
    ShipmentLine.objects.create(
        shipment=shipment,
        order_line=line_item
    )
    ShipmentPiece.objects.create(
        shipment=shipment,
        weight=line_item.variant.get_weight(),
        depth=0.1,
        width=0.1,
        decleared_value=line_item.variant.cost_price,
    )
