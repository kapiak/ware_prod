import logging
import random
import string

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from measurement.measures import Weight
from sequences import get_next_value

from assistant.addresses.models import Address
from assistant.orders.models import LineItem, Order
from assistant.products.models import Product, ProductType, ProductVariant
from assistant.utils.helpers import get_random_string

logger = logging.getLogger(__name__)

User = get_user_model()


@transaction.atomic
def process_order(**data) -> Order:
    customer = data.pop("customer_form")
    shipping = data.pop("shipping_form")
    items = data.pop("product_add_formset")

    address = Address.objects.create(
        first_name=customer["name"],
        city=customer["city"],
        city_area=customer["state"],
        country=customer["country"],
        postal_code=customer["code"],
    )

    if not User.objects.filter(email=customer["email"]):
        user = User.objects.create_user(
            name=customer["name"],
            username=customer["email"],
            email=customer["email"],
            shipping_address=address,
        )

    else:
        raise ValidationError(
            message=_("Email already registered please login to your account"),
            code=_("exists"),
        )

    order = Order.objects.create(
        number=get_next_value("order_number", initial_value=10000),
        customer_email=user.email,
        customer_id=user.pk,
        total_price=100,
        status=Order.StatusChoices.DRAFT,
        type=Order.OrderType.DRAFT,
        user=user,
        billing_address=address,
        shipping_address=address,
    )
    for item in items:
        product_type = ProductType.objects.filter(slug="manual")
        if not product_type.exists():
            product_type = ProductType.objects.create(name="Manual", slug="manual")
        product = Product.objects.create(
            title=item["name"],
            slug=get_random_string(20),  # TODO: This will cause errors and need to fix
            description=item["comments"],
            weight=Weight(kg=shipping["weight"]),
            max_price=item["price"],
            min_price=item["price"],
        )
        variant = ProductVariant.objects.create(
            product=product,
            sku=get_random_string(20),  # TODO: Might Clash need to solve this.
            barcode=get_random_string(30),  # TODO: Might Clash need to solve this.
            name=item["name"],
            price=item["price"],
            weight=Weight(kg=shipping["weight"]),
            metadata={"url": item["url"]},
        )
        LineItem.objects.create(
            order=order,
            variant=variant,
            is_shipping_required=True,
            quantity=item["quantity"],
            metadata={"url": item["url"]},
        )
    return order


@transaction.atomic
def process_order_for_user(user, **data) -> Order:
    customer = data.pop("customer_form")
    shipping = data.pop("shipping_form")
    items = data.pop("product_add_formset")

    address = Address.objects.create(
        first_name=customer["name"],
        city=customer["city"],
        city_area=customer["state"],
        country=customer["country"],
        postal_code=customer["code"],
    )

    order = Order.objects.create(
        number=get_next_value("order_number", initial_value=10000),
        customer_email=user.email,
        customer_id=user.pk,
        total_price=100,
        status=Order.StatusChoices.DRAFT,
        type=Order.OrderType.DRAFT,
        user=user,
        billing_address=address,
        shipping_address=address,
    )
    for item in items:
        product_type = ProductType.objects.filter(slug="manual")
        if not product_type.exists():
            product_type = ProductType.objects.create(name="Manual", slug="manual")
        product = Product.objects.create(
            title=item["name"],
            slug=get_random_string(20),  # TODO: This will cause errors and need to fix
            description=item["comments"],
            weight=Weight(kg=shipping["weight"]),
            max_price=item["price"],
            min_price=item["price"],
        )
        variant = ProductVariant.objects.create(
            product=product,
            sku=get_random_string(20),  # TODO: Might Clash need to solve this.
            barcode=get_random_string(30),  # TODO: Might Clash need to solve this.
            name=item["name"],
            price=item["price"],
            weight=Weight(kg=shipping["weight"]),
            metadata={"url": item["url"]},
        )
        LineItem.objects.create(
            order=order,
            variant=variant,
            is_shipping_required=True,
            quantity=item["quantity"],
            metadata={"url": item["url"]},
        )
    return order
