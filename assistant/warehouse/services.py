import logging

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
                    f"Allocating to order {line_item} but ran out of stock {stock} continue the loop. {ins}"
                )
                continue
    return assigned_to
