import shopify

from config import celery_app

from .models import ShopifySyncLog
from .service import ShopifyService


@celery_app.task()
def get_products_pages():
    """Get Products Pages and Record the result in the Sync."""
    service = ShopifyService()
    for page in service.get_product_pages():
        metadata = {
            "count": len(page)
        }
        if "next_page_url" in page.metadata:
            metadata.update({
                "next_page_url": page.next_page_url,
            })
        if "previous_page_url" in page.metadata:
            metadata.update({
                "previous_page_url": page.previous_page_url,
            })
        ShopifySyncLog.objects.create(
            object_type=ShopifySyncLog.ObjectTypeChoices.PRODUCT,
            metadata=metadata
        )


@celery_app.task()
def get_orders_pages():
    service = ShopifyService()
    for page in service.get_orders_pages():
        metadata = {
            "count": len(page)
        }
        if "next_page_url" in page.metadata:
            metadata.update({
                "next_page_url": page.next_page_url,
            })
        if "previous_page_url" in page.metadata:
            metadata.update({
                "previous_page_url": page.previous_page_url,
            })
        ShopifySyncLog.objects.create(
            object_type=ShopifySyncLog.ObjectTypeChoices.ORDER,
            metadata=metadata
        )


def fetch_first_product_page():
    service = ShopifyService()
    page = service.get_first_product_page()
    metadata = {
        "count": len(page)
    }
    if "next_page_url" in page.metadata:
        metadata.update({
            "next_page_url": page.next_page_url,
        })
    if "previous_page_url" in page.metadata:
        metadata.update({
            "previous_page_url": page.previous_page_url,
        })
    ShopifySyncLog.objects.create(
        object_type=ShopifySyncLog.ObjectTypeChoices.PRODUCT,
        metadata=metadata
    )
