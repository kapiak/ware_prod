import logging

from django.dispatch import receiver
from pydantic import ValidationError

from assistant.products.models import Product, ProductType, ProductVariant

from . import signals
from .models import EventStore
from .schemas import ProductSchema, OrderSchema
from .tasks import (
    process_product_create,
    process_product_update,
    process_order_create,
    process_draft_order_create,
    process_order_update,
    process_order_create,
    process_draft_order_update,
    process_order_fulfilled,
    process_order_partially_fulfilled,
    process_order_paid,
    process_order_cancelled,
)

logger = logging.getLogger(__name__)


@receiver(signals.webhook_received)
def handle_webhook_received(sender, **kwargs):
    logger.info("Signal handle_webhook_received is Running.")


@receiver(signals.products_create)
def handle_product_create(sender, **kwargs):
    # print(sender, **kwargs)
    logger.info("Handling Product Create.")
    domain = kwargs.get('domain')
    topic = kwargs.get('topic')
    data = kwargs.get('data')
    event = kwargs.get('event')
    process_product_create.delay(event.guid, domain, topic, data)


@receiver(signals.products_update)
def handle_product_update(sender, **kwargs):
    # logger.info(sender, **kwargs)
    logger.info("Handling Product Update.")
    domain = kwargs.get('domain')
    topic = kwargs.get('topic')
    data = kwargs.get('data')
    event = kwargs.get('event')
    process_product_update.delay(event.guid, domain, topic, data)


@receiver(signals.products_delete)
def handle_product_delete(sender, **kwargs):
    logger.info("Signal handle_product_delete is Running")


@receiver(signals.orders_create)
def handle_order_create(sender, **kwargs):
    logger.info("Handling Order Create.")
    domain = kwargs.get('domain')
    topic = kwargs.get('topic')
    data = kwargs.get('data')
    event = kwargs.get('event')
    process_order_create.delay(event.guid, domain, topic, data)


@receiver(signals.orders_delete)
def handle_order_delete(sender, **kwargs):
    logger.info("Signal handle_order_delete is Running")


@receiver(signals.orders_updated)
def handle_order_update(sender, **kwargs):
    logger.info("Handling Order Update.")
    domain = kwargs.get('domain')
    topic = kwargs.get('topic')
    data = kwargs.get('data')
    event = kwargs.get('event')
    process_order_update.delay(event.guid, domain, topic, data)


@receiver(signals.orders_paid)
def handle_order_paid(sender, **kwargs):
    logger.info("Handling Order Paid.")
    domain = kwargs.get('domain')
    topic = kwargs.get('topic')
    data = kwargs.get('data')
    event = kwargs.get('event')
    process_order_paid.delay(event.guid, domain, topic, data)


@receiver(signals.orders_cancelled)
def handle_order_cancelled(sender, **kwargs):
    logger.info("Handling Order Cancelled.")
    domain = kwargs.get('domain')
    topic = kwargs.get('topic')
    data = kwargs.get('data')
    event = kwargs.get('event')
    process_order_cancelled.delay(event.guid, domain, topic, data)


@receiver(signals.orders_fulfilled)
def handle_order_fulfilled(sender, **kwargs):
    logger.info("Handling Order Fulfilled.")
    domain = kwargs.get('domain')
    topic = kwargs.get('topic')
    data = kwargs.get('data')
    event = kwargs.get('event')
    process_order_fulfilled.delay(event.guid, domain, topic, data)


@receiver(signals.orders_partially_fulfilled)
def handle_order_partially_fulfilled(sender, **kwargs):
    logger.info("Handling Order Partially Fulfilled.")
    domain = kwargs.get('domain')
    topic = kwargs.get('topic')
    data = kwargs.get('data')
    event = kwargs.get('event')
    process_order_partially_fulfilled.delay(event.guid, domain, topic, data)


@receiver(signals.checkouts_create)
def handler_checkout_create(sender, **kwargs):
    logger.info("Signal handler_checkout_create is Running")


@receiver(signals.checkouts_update)
def handler_checkout_update(sender, **kwargs):
    logger.info("Signal handler_checkout_update is Running")


@receiver(signals.draft_orders_create)
def handler_draft_order_create(sender, **kwargs):
    logger.info("Handling Draft Order Create.")
    domain = kwargs.get('domain')
    topic = kwargs.get('topic')
    data = kwargs.get('data')
    event = kwargs.get('event')
    process_draft_order_create.delay(event.guid, domain, topic, data)


@receiver(signals.draft_orders_update)
def handler_draft_order_update(sender, **kwargs):
    logger.info("Handling Draft Order Update.")
    domain = kwargs.get('domain')
    topic = kwargs.get('topic')
    data = kwargs.get('data')
    event = kwargs.get('event')
    process_draft_order_update.delay(event.guid, domain, topic, data)
