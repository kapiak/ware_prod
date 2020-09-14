import shopify
import random
import string
from decimal import Decimal
from celery.utils.log import get_task_logger
from pydantic import ValidationError

from config import celery_app

from assistant.products.services import (
    create_product,
    update_product,
    create_product_variant,
    update_product_variant,
)
from assistant.products.models import Product, ProductVariant

from .models import ShopifySyncLog, EventStore
from .schemas import OrderSchema, ProductSchema
from .service import ShopifyService

logger = get_task_logger(__name__)


@celery_app.task()
def get_products_pages():
    """Get Products Pages and Record the result in the Sync."""
    service = ShopifyService()
    for page in service.get_product_pages():
        metadata = {"count": len(page)}
        if "next_page_url" in page.metadata:
            metadata.update(
                {"next_page_url": page.next_page_url,}
            )
        if "previous_page_url" in page.metadata:
            metadata.update(
                {"previous_page_url": page.previous_page_url,}
            )
        ShopifySyncLog.objects.create(
            object_type=ShopifySyncLog.ObjectTypeChoices.PRODUCT,
            metadata=metadata,
        )


@celery_app.task()
def get_orders_pages():
    service = ShopifyService()
    for page in service.get_orders_pages():
        metadata = {"count": len(page)}
        if "next_page_url" in page.metadata:
            metadata.update(
                {"next_page_url": page.next_page_url,}
            )
        if "previous_page_url" in page.metadata:
            metadata.update(
                {"previous_page_url": page.previous_page_url,}
            )
        ShopifySyncLog.objects.create(
            object_type=ShopifySyncLog.ObjectTypeChoices.ORDER,
            metadata=metadata,
        )


def fetch_first_product_page():
    service = ShopifyService()
    page = service.get_first_product_page()
    metadata = {"count": len(page)}
    if "next_page_url" in page.metadata:
        metadata.update(
            {"next_page_url": page.next_page_url,}
        )
    if "previous_page_url" in page.metadata:
        metadata.update(
            {"previous_page_url": page.previous_page_url,}
        )
    ShopifySyncLog.objects.create(
        object_type=ShopifySyncLog.ObjectTypeChoices.PRODUCT, metadata=metadata
    )


@celery_app.task()
def process_product_create(event_id, domain, topic, data):
    logger.info("Task is Running.")
    event = EventStore.objects.get(guid=event_id)
    event.status = EventStore.StatusChoices.IN_PROCESS
    event.save(update_fields=["status"])
    try:
        schema = ProductSchema(**data)
        product_obj = create_product(
            **schema.dict(
                include={
                    "vendor",
                    "product_type",
                    "title",
                    "slug",
                    "description",
                }
            ),
            additional_data={"meta": "meta"}
        )
        if not schema.variants:
            output_string = 'NOCODE_' + ''.join(
                random.SystemRandom().choice(
                    string.ascii_letters + string.digits
                )
                for _ in range(10)
            )
            create_product_variant(
                product=product_obj,
                title="Default Variant",
                price=Decimal("0.1"),
                sku=output_string,
                barcode=output_string,
            )
        else:
            for variant in schema.variants:
                create_product_variant(
                    **variant.dict(
                        include={"title", "price", "sku", "barcode"}
                    )
                )
        event.status = EventStore.StatusChoices.SUCCESS
        event.save(update_fields=["status"])
    except ValidationError as e:
        event.status = EventStore.StatusChoices.FAILED
        event.error_data = e.json()
        event.save(update_fields=["status", "error_data"])
        logger.exception(
            "Shopify Webhook Handling Product Create Validation Error: %s",
            e.json(),
        )


@celery_app.task()
def process_product_update(event_id, domain, topic, data):
    logger.info("Task is Running.")
    event = EventStore.objects.get(guid=event_id)
    event.status = EventStore.StatusChoices.IN_PROCESS
    event.save(update_fields=["status"])
    try:
        schema = ProductSchema(**data)
        product_obj = Product.objects.get(metadata__shopify_id=schema.id)
        update_product(
            product=product_obj,
            **schema.dict(
                include={
                    "vendor",
                    "product_type",
                    "title",
                    "slug",
                    "description",
                }
            )
        )
        if not schema.variants:
            output_string = 'NOCODE_' + ''.join(
                random.SystemRandom().choice(
                    string.ascii_letters + string.digits
                )
                for _ in range(10)
            )
            create_product_variant(
                product=product_obj,
                title="Default Variant",
                price=Decimal("0.1"),
                sku=output_string,
                barcode=output_string,
            )
        else:
            for variant in schema.variants:
                variant_obj = ProductVariant.objects.get(
                    metadata__shopify_id=variant.id
                )
                update_product_variant(
                    variant=variant_obj,
                    **variant.dict(
                        include={"title", "price", "sku", "barcode"}
                    )
                )
    except ValidationError as e:
        event.status = EventStore.StatusChoices.FAILED
        event.error_data = e.json()
        event.save(update_fields=["status", "error_data"])
        logger.exception(
            "Shopify Webhook Handling Product Update Validation Error: %s",
            e.json(),
        )


@celery_app.task()
def process_order_create(event_id, domain, topic, data):
    logger.info("Task is Running.")
    # event = EventStore.objects.filter(guid=event_id).update(status=EventStore.StatusChoices.RECEIVED)
    try:
        schema = OrderSchema(**data)
    except ValidationError as e:
        logger.exception(
            "Shopify Webhook Handling Order Create Validation Error: %s",
            e.json(),
        )


@celery_app.task()
def process_draft_order_create(event_id, domain, topic, data):
    logger.info("Task is Running.")
    # event = EventStore.objects.filter(guid=event_id).update(status=EventStore.StatusChoices.RECEIVED)
    try:
        schema = OrderSchema(**data)
    except ValidationError as e:
        logger.exception(
            "Shopify Webhook Handling Draft Order Create Validation Error: %s",
            e.json(),
        )


@celery_app.task()
def process_order_update(event_id, domain, topic, data):
    logger.info("Task is Running.")
    # event = EventStore.objects.filter(guid=event_id).update(status=EventStore.StatusChoices.RECEIVED)
    try:
        schema = OrderSchema(**data)
    except ValidationError as e:
        logger.exception(
            "Shopify Webhook Handling Order Update Validation Error: %s",
            e.json(),
        )


@celery_app.task()
def process_draft_order_update(event_id, domain, topic, data):
    logger.info("Task is Running.")
    # event = EventStore.objects.filter(guid=event_id).update(status=EventStore.StatusChoices.RECEIVED)
    try:
        schema = OrderSchema(**data)
    except ValidationError as e:
        logger.exception(
            "Shopify Webhook Handling Draft Order Update Validation Error: %s",
            e.json(),
        )


@celery_app.task()
def process_order_paid(event_id, domain, topic, data):
    logger.info("Task is Running.")
    # event = EventStore.objects.filter(guid=event_id).update(status=EventStore.StatusChoices.RECEIVED)
    try:
        schema = OrderSchema(**data)
    except ValidationError as e:
        logger.exception(
            "Shopify Webhook Handling Order Paid Validation Error: %s",
            e.json(),
        )


@celery_app.task()
def process_order_fulfilled(event_id, domain, topic, data):
    logger.info("Task is Running.")
    # event = EventStore.objects.filter(guid=event_id).update(status=EventStore.StatusChoices.RECEIVED)
    try:
        schema = OrderSchema(**data)
    except ValidationError as e:
        logger.exception(
            "Shopify Webhook Handling Order Fulfilled Validation Error: %s",
            e.json(),
        )


@celery_app.task()
def process_order_partially_fulfilled(event_id, domain, topic, data):
    logger.info("Task is Running.")
    # event = EventStore.objects.filter(guid=event_id).update(status=EventStore.StatusChoices.RECEIVED)
    try:
        schema = OrderSchema(**data)
    except ValidationError as e:
        logger.exception(
            "Shopify Webhook Handling Order Partially Fulfilled Validation Error: %s",
            e.json(),
        )


@celery_app.task()
def process_order_cancelled(event_id, domain, topic, data):
    logger.info("Task is Running.")
    # event = EventStore.objects.filter(guid=event_id).update(status=EventStore.StatusChoices.RECEIVED)
    try:
        schema = OrderSchema(**data)
    except ValidationError as e:
        logger.exception(
            "Shopify Webhook Handling Order Cancelled Validation Error: %s",
            e.json(),
        )
