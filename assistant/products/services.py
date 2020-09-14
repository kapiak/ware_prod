import uuid
import logging

from typing import Optional, Dict, Union, List
from decimal import Decimal
from .models import Vendor, ProductType, Product, ProductVariant, Supplier
from assistant.shopify_sync.schemas import VariantSchema


logger = logging.getLogger(__name__)


def create_vendor(*, name: str) -> Vendor:
    obj = Vendor.objects.create(name=name)
    return obj


def create_product_type(
    *, name: str, slug: Optional[str] = None
) -> ProductType:
    obj = ProductType.objects.create(name=name)
    if slug:
        obj.slug = slug
        obj.save()
    return obj


def create_product_variant(
    *,
    product: Product,
    title: str,
    price: Decimal,
    sku: Optional[str],
    barcode: Optional[str]
) -> ProductVariant:
    obj = ProductVariant.objects.create(
        product=product, name=title, price=price,
    )
    if sku:
        obj.sku = sku
    if barcode:
        obj.barcode = barcode
    obj.save(update_fields=['sku', 'barcode'])
    return obj


def update_product_variant(
    *,
    variant: Optional[Union[uuid.UUID, ProductVariant]],
    title: str,
    price: Decimal,
    sku: Optional[str],
    barcode: Optional[str]
) -> ProductVariant:
    if isinstance(variant, uuid.UUID):
        try:
            variant = ProductVariant.objects.get(guid=variant)
        except ProductVariant.DoesNotExist as e:
            logger.exception("Can't find Variant with uuid %s", e)
    variant.title = title
    variant.price = price
    if variant.sku:
        variant.sku = sku
    if variant.barcode:
        variant.barcode = barcode
    variant.save()
    return variant


def create_product(
    *,
    vendor: Union[str, Vendor],
    product_type: Union[str, ProductType],
    title: str,
    slug: Optional[str],
    description: Optional[str],
    additional_data: Optional[Dict]
) -> Product:
    if isinstance(vendor, str):
        vendor = create_vendor(name=vendor)
    if isinstance(product_type, str):
        product_type = create_product_type(name=product_type)
    obj = Product.objects.create(
        vendor=vendor, product_type=product_type, title=title,
    )
    if slug:
        obj.slug = slug
    if description:
        obj.description = description
    obj.save(update_fields=['slug', 'description'])
    return obj


def update_product(
    *,
    product: Union[uuid.UUID, Product],
    vendor: Union[str, Vendor],
    product_type: Union[str, ProductType],
    title: str,
    slug: Optional[str],
    description: Optional[str],
    variants: Optional[List[Union[VariantSchema, ProductVariant]]],
    additional_data: Optional[Dict]
) -> Product:
    if isinstance(vendor, str):
        try:
            vendor = Vendor.objects.get(name=vendor)
        except Vendor.DoesNotExist:
            vendor = create_vendor(name=vendor)

    if isinstance(product_type, str):
        try:
            product_type = ProductType.objects.get(name=product_type)
        except ProductType.DoesNotExist:
            product_type = create_product_type(name=product_type)

    if isinstance(product, uuid.UUID):
        try:
            product = Product.objects.get(guid=product)
        except Product.DoesNotExist as e:
            logger.exception("Couldn't find product with uuid %s", e)
    product.title = title
    product.vendor = vendor
    product.product_type = product_type
    if slug:
        product.slug = slug
    if description:
        product.description = description
    product.save()
    return product
