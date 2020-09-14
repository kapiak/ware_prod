import logging

from django.dispatch import receiver

from assistant.shipping.models import Shipment, ShipmentLine, ShipmentPiece

from sequences import get_next_value

from .models import Stock
from .signals import allocated_stock, stock_increased
from .tasks import allocate_stock_task, create_shipment_task

logger = logging.getLogger(__name__)


@receiver(stock_increased, sender=Stock)
def on_stock_added(sender, instance, **kwargs):
    logger.info('On Stock Added Signal: Sender: %s -> Instance: %s -> Kwargs: %s', sender, instance, kwargs)
    allocate_stock_task.delay(guid=instance.product_variant.guid)


@receiver(allocated_stock, sender=Stock)
def handle_fully_allocated_orders(sender, instance, **kwargs):
    logger.info('On Stock Fully Allocated Signal: Sender: %s -> Instance: %s -> Kwargs: %s', sender, instance, kwargs)
    line_item = kwargs['line_item']
    if line_item.fully_allocated:
        logger.info("The order is fully allocated and shipment is being prepared.")
        create_shipment_task.delay(guid=line_item.guid)
    else:
        logger.info("The order is not fully allocated")
