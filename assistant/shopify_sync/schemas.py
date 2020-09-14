from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class VariantSchema(BaseModel):
    variant_id: Optional[str]
    product_id: Optional[str]
    title: str
    price: Decimal
    sku: Optional[str]
    barcode: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProductSchema(BaseModel):
    id: str
    title: str
    vendor: str
    product_type: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    tags: Optional[str]
    variants: Optional[List[VariantSchema]]

    class Config:
        orm_mode = True


class OrderLineSchema(BaseModel):
    id: Optional[str]
    variant_id: Optional[str]
    quantity: int

    class Config:
        orm_mode = True


class AddressSchema(BaseModel):
    first_name: str
    last_name: str
    address1: str
    address2: Optional[str]
    city: Optional[str]
    zip: str
    province: Optional[str]
    country_code: str
    company: Optional[str]

    class Config:
        orm_mode = True


class CustomerSchema(BaseModel):
    id: str
    email: str
    created_at: datetime
    updated_at: datetime
    status: Optional[str]

    class Config:
        orm_mode = True


class OrderSchema(BaseModel):
    id: str
    email: str
    number: Optional[int]
    token: Optional[str]
    total_price: Decimal
    subtotal_price: Decimal
    financial_status: Optional[str]
    confirmed: Optional[bool]
    name: str
    notes: Optional[str]
    cancelled_at: Optional[datetime]
    cancel_reason: Optional[str]
    user_id: Optional[int]
    customer: Optional[CustomerSchema]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]
    shipping_address: Optional[AddressSchema]
    billing_address: Optional[AddressSchema]
    line_items: List[OrderLineSchema]

    class Config:
        orm_mode = True
