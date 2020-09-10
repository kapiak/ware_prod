from django.dispatch import receiver

from . import signals


@receiver(signals.products_create)
def handle_product_create(sender, **kwargs):
    print(sender, **kwargs)



@receiver(signals.products_update)
def handle_product_update(sender, **kwargs):
    print(sender, **kwargs)



@receiver(signals.products_delete)
def handle_product_delete(sender, **kwargs):
    print(sender, **kwargs)
    


@receiver(signals.orders_create)
def handle_order_create(sender, **kwargs):
    print(sender, kwargs)


@receiver(signals.orders_delete)
def handle_order_delete(sender, **kwargs):
    print(sender, kwargs)


@receiver(signals.orders_updated)
def handle_order_update(sender, **kwargs):
    print(sender, kwargs)


@receiver(signals.orders_paid)
def handle_order_paid(sender, **kwargs):
    print(sender, kwargs)


@receiver(signals.orders_cancelled)
def handle_order_cancelled(sender, **kwargs):
    print(sender, kwargs)


@receiver(signals.orders_fulfilled)
def handle_order_fulfilled(sender, **kwargs):
    print(sender, kwargs)


@receiver(signals.orders_partially_fulfilled)
def handle_order_partially_fulfilled(sender, **kwargs):
    print(sender, kwargs)


@receiver(signals.order_transactions_create)
def handle_order_transactions_create(sender, **kwargs):
    print(sender, kwargs)


@receiver(signals.checkouts_create)
def handler_checkout_create(sender, **kwargs):
    print(sender, kwargs)


@receiver(signals.checkouts_update)
def handler_checkout_update(sender, **kwargs):
    print(sender, kwargs)


@receiver(signals.draft_orders_create)
def handler_draft_order_create(sender, **kwargs):
    print(sender, kwargs)



@receiver(signals.draft_orders_update)
def handler_draft_order_update(sender, **kwargs):
    print(sender, kwargs)

