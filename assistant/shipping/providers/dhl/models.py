from typing import Dict, List

from pydantic import BaseModel


class Address(BaseModel):
    """Shipping Party Address (Contact and Address) Type"""

    id: str = None
    postal_code: str = None
    city: str = None
    federal_tax_id: str = None
    state_tax_id: str = None
    person_name: str = None
    company_name: str = None
    country_code: str = None
    email: str = None
    phone_number: str = None

    state_code: str = None
    suburb: str = None
    residential: bool = False

    address_line1: str = ""
    address_line2: str = ""



class Commodity(BaseModel):
    """item type is a commodity."""

    id: str = None
    weight: float = None
    width: float = None
    height: float = None
    length: float = None
    description: str = None
    quantity: int = 1
    sku: str = None
    value_amount: float = None
    value_currency: str = None
    origin_country: str = None


class Parcel(BaseModel):
    """item type."""

    id: str = None
    weight: float = None
    width: float = None
    height: float = None
    length: float = None
    packaging_type: str = None
    package_preset: str = None
    description: str = None
    content: str = None
    is_document: bool = False
    weight_unit: str = None
    dimension_unit: str = None


class Invoice(BaseModel):
    """invoice type."""

    date: str
    identifier: str = None
    type: str = None
    copies: int = None


class Card(BaseModel):
    """Credit Card type."""

    type: str
    number: str
    expiry_month: str
    expiry_year: str
    security_code: str
    name: str = None
    postal_code: str = None


class Payment(BaseModel):
    """payment configuration type."""

    paid_by: str = "sender"
    amount: float = None
    currency: str = None
    account_number: str = None
    credit_card: Card = Card
    contact: Address = Address


class Customs:
    """customs type."""

    no_eei: str = None
    aes: str = None
    description: str = None
    terms_of_trade: str = None
    commodities: List[Commodity] = List[Commodity]
    duty: Payment = Payment
    invoice: Invoice = Invoice
    commercial_invoice: bool = False


class Doc(BaseModel):
    """document image type."""

    type: str = None
    format: str = None
    image: str = None


class ShipmentRequest:
    """shipment request type."""

    service: str

    shipper: Address = Address
    recipient: Address = Address
    parcel: Parcel = Parcel

    payment: Payment = Payment
    customs: Customs = Customs
    doc_images: List[Doc] = List[Doc]

    options: Dict = {}
    reference: str = ""


class RateRequest(BaseModel):
    shipper: Address = Address
    recipient: Address = Address
    parcel: Parcel = Parcel
    services: List[str] = []
    options: Dict = {}
    reference: str = ""


class TrackingRequest(BaseModel):
    """tracking request type."""

    tracking_numbers: List[str]
    language_code: str = None
    level_of_details: str = None


class PickupRequest(BaseModel):
    """pickup request type."""

    date: str
    address: Address = Address
    parcels: List[Parcel] = List[Parcel]
    ready_time: str = None
    closing_time: str = None
    instruction: str = None
    package_location: str = None


class PickupUpdateRequest(BaseModel):
    """pickup update request type."""

    date: str
    address: Address = Address
    parcels: List[Parcel] = List[Parcel]
    confirmation_number: str = None
    ready_time: str = None
    closing_time: str = None
    instruction: str = None
    package_location: str = None


class PickupCancellationRequest(BaseModel):
    """pickup cancellation request type."""

    pickup_date: str
    confirmation_number: str
    person_name: str = None
    country_code: str = None


class COD(BaseModel):
    """cash on delivery option type."""

    amount: float


class Notification(BaseModel):
    """notification option type."""

    email: str = None  # Only defined if other email than shipper
    locale: str = "en"


class Insurance(BaseModel):
    """insurance option type."""

    amount: float

class Message(BaseModel):
    """Message type."""

    carrier_name: str
    carrier_id: str
    message: str = None
    code: str = None
    details: Dict = None


class ChargeDetails(BaseModel):
    """charge type."""

    name: str = None
    amount: float = None
    currency: str = None


class TrackingEvent(BaseModel):
    """tracking event type."""

    date: str
    description: str
    location: str
    code: str = None
    time: str = None
    signatory: str = None


class RateDetails(BaseModel):
    """rate (quote) details type."""

    carrier_name: str
    carrier_id: str
    currency: str
    transit_days: int = None
    service: str = None
    discount: float = None
    base_charge: float = 0.0
    total_charge: float = 0.0
    duties_and_taxes: float = None
    extra_charges: List[ChargeDetails] = []
    id: str = None


class TrackingDetails(BaseModel):
    """tracking details type."""

    carrier_name: str
    carrier_id: str
    tracking_number: str
    events: List[TrackingEvent] = []


class ShipmentDetails(BaseModel):
    """shipment details type."""

    carrier_name: str
    carrier_id: str
    label: str
    tracking_number: str
    selected_rate: RateDetails = None
    id: str = None


class PickupDetails(BaseModel):
    """pickup details type."""

    carrier_name: str
    carrier_id: str
    confirmation_number: str
    pickup_date: str = None
    pickup_charge: ChargeDetails = None
    ready_time: str = None
    closing_time: str = None
    id: str = None