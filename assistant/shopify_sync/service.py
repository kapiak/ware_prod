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
from sequences import get_next_value
from django.contrib.auth import get_user_model
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
from assistant.warehouse.models import Stock, Warehouse
from assistant.addresses.models import Address
from .models import ShopifySyncLog, ErrorSyncLog

logger = logging.getLogger(__name__)

User = get_user_model()


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
        logger.info(product.to_dict())
    
        vendor, _ = Vendor.objects.get_or_create(
            name=product.vendor,
        )
        try:
            product_type, _ = ProductType.objects.get_or_create(
                name=product.product_type,
                slug=slugify(product.product_type)
            )
        except IntegrityError as ie:
            logger.exception("Yeah some duplicate slug. generate a new one")
            output_string = 'NOCODE_' + ''.join(
                random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10)
            )
            product_type, _ = ProductType.objects.get_or_create(
                name=product.product_type,
                slug=output_string
            )
        variants = []
        product_by_handle = Product.objects.filter(slug=product.handle)
        product_by_id = Product.objects.filter(metadata__shopify_id=product.id)
        if product_by_handle.exists():
            product_obj = product_by_handle
        if product_by_id.exists():
            product_obj = product_by_id
        if not product_by_handle.exists() or product_by_id.exists():
            try:
                product_obj, _ = Product.objects.get_or_create(
                    vendor=vendor,
                    product_type=product_type,
                    title=product.title,
                    slug=product.handle,
                    description=product.body_html,
                    max_price=0,
                    min_price=0,
                    metadata={
                        "shopify_id": product.id,
                        "shopify_tags": product.tags,
                    }
                )
            except IntegrityError as ie:
                logger.info("Issue with sync")
                ErrorSyncLog.objects.create(
                    metadata={
                        "type": "product",
                        "errors": str(ie),
                        "data": product.to_dict()
                    }
                )
        prices = []
        for variant in product.variants:
            logger.info(variant.to_dict())
            variant_exists_by_id = ProductVariant.objects.filter(
                metadata__shopify_id=variant.id
            ).exists()
            output_string = 'NOCODE_' + ''.join(
                random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10)
            )
            if not variant_exists_by_id:
                prices.append(variant.price)
                try:
                    variant_obj = ProductVariant.objects.create(
                        sku=variant.sku if variant.sku else variant.id,
                        barcode=variant.barcode if variant.barcode else output_string,
                        price=variant.price,
                        cost_price=variant.price,
                        product=product_obj,
                        weight=Weight(lb=variant.weight),
                        metadata={
                            "shopify_id": variant.id,
                            "shopify_inventory_item_id": variant.inventory_item_id,
                        }
                    )
                    variants.append(variant_obj)
                    max_price = max(*prices)
                    min_price = min(*prices)
                    try:
                        product_obj.max_price = max_price
                        product_obj.min_price = min_price
                        product_obj.save()
                    except ValidationError as e:
                        logger.exception("The value isn't valid. moving on %s", e)
                    stock = Stock.objects.create(
                        warehouse=Warehouse.objects.first(),
                        product_variant=variant_obj,
                        quantity=0,
                    )
                    if variant.inventory_quantity > 0:
                        logger.info("Inventory is Positive")
                        stock.increase_stock(
                            quantity=variant.inventory_quantity,
                            commit=True
                        )
                    else:
                        logger.info("Negative Inventory")
                except IntegrityError as ie:
                    logger.info("Issue with sync")
                    ErrorSyncLog.objects.create(
                        metadata={
                            "type": "variant",
                            "errors": str(ie),
                            "data": variant.to_dict()
                        }
                    )

    def get_product_pages(self):
        page = shopify.Product.find(limit=250)
        if page:
            yield page
        while page.has_next_page():
            page = page.next_page()
            yield page

    def get_orders_pages(self):
        page = shopify.Order.find(limit=250)
        if page:
            yield page
        while page.has_next_page():
            page = page.next_page()
            yield page

    def get_first_product_page(self):
        page = shopify.Product.find(limit=250)
        return page
                    
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
        page = shopify.Order.find(limit=250)
        if page:
            for order in page:
                self._populate_order(order)
        while page.has_next_page():
            page = page.next_page()
            for order in page:
                self._populate_order(order)


    def _populate_order(self, order):
        try:
            order_object = Order.objects.get(metadata__shopify_id=order.id)
            logger.info("Order Already exists. %s", order_object)
        except Order.DoesNotExist as de:
            logger.info("New Order: %s", de)
            logger.info(order.to_dict())
            order_object = Order.objects.create(
                number=get_next_value("order_number", initial_value=10000),
                customer_email=order.email,
                total_price=order.total_price,
                subtotal_price=order.subtotal_price,
                total_tax=order.total_tax,
                financial_status=order.financial_status,
                cancel_reason=order.cancel_reason if order.cancel_reason else '',
                cancelled_at=order.cancelled_at,
                closed_at=order.closed_at,
                status=order.fulfillment_status or Order.StatusChoices.UNFULFILLED,
            )
            logger.info("Order Created %s", order_object.guid)

        billing_address = None

        if "billing_address" in order.attributes:
            try:
                address1 = order.billing_address.address1
                billing_address = Address.objects.filter(
                    street_address_1=order.billing_address.address1,
                    postal_code=order.billing_address.zip
                )
                logger.info("Billing Address Already exists ? %s", billing_address.exists())
            except AttributeError:
                logger.info("No Billing address")
                billing_address = Address.objects.none()
            if not billing_address.exists():
                logger.info("creating new Billing address")
                billing_address = Address.objects.create(
                    first_name=order.billing_address.first_name,
                    last_name=order.billing_address.last_name,
                    street_address_1=order.billing_address.address1 or "NULL",
                    street_address_2=order.billing_address.address2 or "",
                    city=order.billing_address.city,
                    postal_code=order.billing_address.zip or "",
                    city_area=order.billing_address.province or "",
                    country=order.billing_address.country_code,
                    company_name=order.billing_address.company or "",
                )
            else:
                billing_address = billing_address.first()
            order_object.billing_address = billing_address
        
        shipping_address = None

        if "shipping_address" in order.attributes:
            try:
                address1 = order.shipping_address.address1
                shipping_address = Address.objects.filter(
                    street_address_1=address1,
                    postal_code=order.shipping_address.zip
                )
                logger.info("Shipping Address Already exists ? %s", billing_address.exists())
            except AttributeError:
                logger.info("No shipping address")
                shipping_address = Address.objects.none()
            if not shipping_address.exists():
                logger.info("creating new Billing address")
                shipping_address = Address.objects.create(
                    first_name=order.shipping_address.first_name,
                    last_name=order.shipping_address.last_name,
                    street_address_1=order.shipping_address.address1 or "NULL",
                    street_address_2=order.shipping_address.address2 or "",
                    city=order.shipping_address.city,
                    postal_code=order.shipping_address.zip or "",
                    city_area=order.shipping_address.province or "",
                    country=order.shipping_address.country_code,
                    company_name=order.shipping_address.company or "",
                )
            else:
                shipping_address = shipping_address.first()
            order_object.shipping_address = shipping_address

        order_object.metadata = {
            "shopify_id": order.id,
            "shopify_order_number": order.number,
            "token": order.token,
            "confirmed": order.confirmed,
            "reference": order.reference,
            "source_identifier": order.source_identifier,
        }
        logger.info("Meta Data Added")
        if "customer" in order.attributes:
            logger.info("Order has a customer")
            customer = User.objects.filter(
                email=order.customer.email
            )
            logger.info("User Exists ? %s", customer.exists())
            if not customer.exists():
                logger.info("Customer does not exists. creating one.")
                first_name = order.customer.first_name
                if len(order.customer.first_name) > 150:
                    trunc_first_name = order.customer.first_name[:150]
                    first_name = trunc_first_name
                last_name = order.customer.last_name
                if len(order.customer.last_name) > 150:
                    trunc_last_name = order.customer.last_name[:150]
                    last_name = trunc_last_name
                customer = User.objects.create(
                    email=order.customer.email,
                    username=order.customer.email,
                    first_name=first_name,
                    last_name=last_name,
                    name=first_name + ' ' + last_name,
                )
                if shipping_address:
                    customer.shipping_address = shipping_address
                if billing_address:
                    customer.billing_address = billing_address
                customer.save()
                logger.info("Customer created %s", customer.email)
            else:
                logger.info("Customer already exists.")
                customer = customer.get()
            order_object.customer = customer
            logger.info("Adding customer to order.")
            order_object.save()
            logger.info("Order Saved.")
        else:
            logger.info("Order %s doesn't have a customer", order.to_dict())

        order_object.save()
        logger.info("Creating line items")
        for line_item in order.line_items:
            logger.info(("Looking for the line item if it exists."))
            line_item_obj = LineItem.objects.filter(
                metadata__shopify_id=line_item.id
            )
            
            logger.info(("Looking for the variant if it exists."))
            variant = ProductVariant.objects.filter(
                metadata__shopify_id=line_item.variant_id
            )
            variant_exists = variant.exists()
            logger.info("variant exists ? %s", variant.exists())
            if not variant_exists:
                logger.info("Couldn't find the Variant")
                ErrorSyncLog.objects.create(
                    metadata={
                        "type": "order_line_item",
                        "message": "Variant Does not Exists",
                        "line_item": line_item.to_dict()
                    }
                )
            else:
                variant = variant.first()
                logger.info("Variant is %s", variant)
                if not line_item_obj.exists():
                    logger.info("LineItem does not exists")
                    try:
                        logger.info("Creating the line item. %s", line_item.to_dict())
                        line_item_obj = LineItem.objects.create(
                            order=order_object,
                            variant=variant,
                            quantity=line_item.quantity,
                            is_shipping_required=line_item.requires_shipping,
                            metadata={
                                "shopify_id": line_item.id,
                            }
                        )
                        logger.info("Created line_item %s", line_item_obj.guid)
                    except Exception as e:
                        logger.info("Error creating line item %s", e)
                        ErrorSyncLog.objects.create(
                            metadata={
                                "type": "order_line_item",
                                "message": "Couldn't create the line_item",
                                "line_item": line_item.to_dict(),
                                "error": e.__str__()
                            }
                        )
                else:
                    ErrorSyncLog.objects.create(
                        metadata={
                            "type": "order_line_item",
                            "message": "Variant Does not Exists",
                            "line_item": line_item.to_dict()
                        }
                    )
