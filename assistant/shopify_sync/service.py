from typing import List
import logging
import random
import string 
from decimal import Decimal

from config.settings.base import (
    SHOPIFY_API_KEY,
    SHOPIFY_API_VERSION,
    SHOPIFY_PASSWORD,
)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from django.db import transaction, DatabaseError
from django.db.utils import IntegrityError

import shopify
from pydantic import BaseModel  #, EmailStr
from measurement.measures import Weight

from assistant.products.models import Vendor, ProductType, Product, ProductVariant
from assistant.orders.models import Order, LineItem
from .models import ShopifySyncLog

logger = logging.getLogger(__name__)


class LineItemSchema(BaseModel):
    """Represents the nested list of line items in Shopify Response."""
    variant: str
    quantity: int

    class Config:
        orm_mode = True


class OrderSchema(BaseModel):
    """The serializer of Shopify Response."""
    id: str
    email: str
    total_price: Decimal
    subtotal_price: Decimal
    total_tax: Decimal
    lines_items: List[LineItemSchema]

    class Config:
        orm_mode = True


class ShopifyService:
    """A helper service to easy the work with the shopify api client."""
    
    def __init__(self):
        self.shop_url = f"https://{settings.SHOPIFY_API_KEY}:{settings.SHOPIFY_PASSWORD}@{settings.SHOPIFY_STORE_NAME}.myshopify.com/admin/api/{settings.SHOPIFY_API_VERSION}/"
        self.session = shopify.Session(
            settings.SHOPIFY_STORE_URL,
            settings.SHOPIFY_API_VERSION,
            settings.SHOPIFY_API_KEY,
        )
        shopify.ShopifyResource.set_site(self.shop_url)
        self.shop = shopify.Shop.current()

    def _populate_product(self, product):
        with transaction.atomic():
            vendor, _ = Vendor.objects.get_or_create(
                name=product.vendor,
            )
            try:
                product_type, _ = ProductType.objects.get_or_create(
                    name=product.product_type,
                    slug=slugify(product.product_type)
                )
            except IntegrityError as ie:
                logger.exception(f"Yeah some duplicate slug. generate a new one")
                output_string = 'NOCODE_' + ''.join(
                        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10)
                    )
                product_type, _ = ProductType.objects.get_or_create(
                    name=product.product_type,
                    slug=output_string
                )
            variants = []
            exists = Product.objects.filter(slug=product.handle).exists()
            if not exists:
                product_obj, _ = Product.objects.get_or_create(
                    vendor=vendor,
                    product_type=product_type,
                    title=product.title,
                    slug=product.handle,
                    description=product.body_html,
                    max_price=0,
                    min_price=0,
                )
                prices = []
                for variant in product.variants:
                    output_string = 'NOCODE_' + ''.join(
                        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10)
                    )
                    prices.append(variant.price)
                    variant_obj = ProductVariant.objects.create(
                        sku=variant.sku if variant.sku else variant.id,
                        barcode=variant.barcode if variant.barcode else output_string,
                        price=variant.price,
                        cost_price=variant.price,
                        product=product_obj,
                        weight=Weight(lb=variant.weight)
                    )
                    variants.append(variant_obj)
                max_price = max(*prices)
                min_price = min(*prices)
                try:
                    product_obj.max_price = max_price
                    product_obj.min_price = min_price
                    product_obj.save()
                except ValidationError as e:
                    logger.exception(f"The value isn't valid. moving on {e}")

    def _sync_in_products_and_variants(self):
        page = shopify.Product.find(limit=250)
        if page:
            for product in page:
                self._populate_product(product)
        while page.has_next_page():
            page = page.next_page()
            for product in page:
                self._populate_product(product) 
                
    def get_orders(self):
        log = ShopifySyncLog.objects.create(
            status=ShopifySyncLog.SyncStatus.STARTED
        )
        try:
            orders = shopify.Order.find(limit=250)
            log.status = ShopifySyncLog.SyncStatus.SUCCEEDED
            log.updated_data = timezone.now()
            log.save()
            if orders:
                for order in orders:
                    with transaction.atomic():
                        order_object = Order.objects.create(
                            number=order.number,
                            customer_email=order.email,
                            total_price=order.total_price,
                            subtotal_price=order.subtotal_price,
                            total_tax=order.total_tax,
                            financial_status=order.financial_status,
                            cancel_reason=order.cancel_reason if order.cancel_reason else '',
                            cancelled_at=order.cancelled_at,
                            closed_at=order.closed_at
                        )
                        for line_item in order.line_items:
                            variant_exists = ProductVariant.objects.filter(
                                product__title=line_item.title
                            ).exists()
                            if variant_exists:
                                line_item_obj = LineItem.objects.create(
                                    order=order_object,
                                    variant=ProductVariant.objects.filter(
                                        product__title=line_item.title
                                    ).first(),
                                    quantity=line_item.quantity,
                                    is_shipping_required=line_item.requires_shipping
                                )
        except Exception as e:  # To broad need to figure out what e does this throw
            logger.exception(f"Error: {e}")
            log.status = ShopifySyncLog.SyncStatus.FAILED
            log.save()