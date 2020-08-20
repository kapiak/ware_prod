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

logger = logging.getLogger(__name__)

User = get_user_model()


@transaction.atomic
def process_order(**data) -> Order:
    customer = data.pop("customer")
    shipping = data.pop("shipping")
    items = data.pop("items")
    address = Address.objects.create(
        first_name=customer["name"],
        city=customer["city"],
        city_area=customer["state"],
        country=customer["country"],
        postal_code=customer["code"],
    )
    username = slugify(customer["name"])
    if User.objects.filter(username=username).exists():
        random_string = "".join(
            [random.choice(string.ascii_letters + string.digits) for n in range(5)]
        )
        username = username + random_string
    if not User.objects.filter(email=customer["email"]):
        user = User.objects.create_user(
            name=customer["name"],
            username=slugify(username),
            email=customer["email"],
            password=customer["password"],
            shipping_address=address,
        )
    else:
        raise ValidationError(message=_("Email Already Registered"), code=_("exists"))
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
            slug=slugify(item["name"]),  # TODO: This will cause errors and need to fix
            description=item["comments"],
            weight=Weight(kg=shipping["weight"]),
            max_price=item["price"],
            min_price=item["price"],
        )
        variant = ProductVariant.objects.create(
            product=product,
            sku=item["url"],  # TODO: Might Clash need to solve this.
            barcode=item["url"],  # TODO: Might Clash need to solve this.
            name=item["name"],
            price=item["price"],
            weight=Weight(kg=shipping["weight"]),
        )
        LineItem.objects.create(
            order=order,
            variant=variant,
            is_shipping_required=True,
            quantity=item["quantity"],
        )
    return order
