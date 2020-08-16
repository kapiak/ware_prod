class InsufficientStock(Exception):
    """Arguments: Order Line Item and a dictrionay context"""

    def __init__(self, item, context=None):
        super().__init__("Insufficient stock for %r" % (item,))
        self.item = item
        self.context = context
        self.code = "insufficient_stock"


class AllocationError(Exception):
    """Arguments: Order Line Item and quantity."""

    def __init__(self, order_line, quantity):
        super().__init__(
            f"Can't deallocate {quantity} for variant: {order_line.variant}"
            f" in order: {order_line.order}"
        )
        self.order_line = order_line
        self.quantity = quantity
