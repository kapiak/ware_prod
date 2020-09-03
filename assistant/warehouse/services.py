import logging
import uuid

from assistant.orders.models import LineItem

from .models import Stock
from .exceptions import InsufficientStock

logger = logging.getLogger(__name__)


def process_simple_stock_allocation(**data):
    stocks = Stock.objects.filter(product_variant=data.get("variant"))
    line_items = data.get("orders", None)
    assigned_to = []
    for line_item in line_items:
        quantity_required = line_item.quantity_unfulfilled
        for stock in stocks:
            try:
                done = stock.allocate_to_order_line_item(
                    line_item=line_item, quantity=quantity_required
                )
                if done:
                    assigned_to.append(line_item)
            except InsufficientStock as ins:
                logger.info(
                    "Allocating to order %s but ran out of stock %s continue the loop. %s",
                    line_item,
                    stock,
                    ins
                )
                continue
    return assigned_to


def allocate_stock(guid: uuid.UUID) -> Stock:
    stocks = Stock.objects.filter(product_variant__guid=guid)
    lines_items = LineItem.objects.filter(variant__guid=guid)
    for item in lines_items:
        for stock in stocks:
            try:
                stock.allocate_to_order_line_item(
                    line_item=item,
                )
            except InsufficientStock as ins:
                logger.info(
                    "Allocating to order %s but ran out of stock %s continue the loop. %s",
                    item,
                    stock,
                    ins
                )
    return stocks
