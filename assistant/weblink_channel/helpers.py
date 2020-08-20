import logging
import random
import string
from decimal import Decimal

import extruct
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from measurement.measures import Weight
from sequences import get_next_value
from wagtail.contrib.modeladmin.helpers import (
    AdminURLHelper,
    ButtonHelper,
    PermissionHelper,
)

from assistant.addresses.models import Address
from assistant.products.models import Product, ProductType, ProductVariant, Supplier
from assistant.orders.models import Order, LineItem

from .models import PurchaseOrder, PurchaseOrderItem, WebLinkOrder, WebLinkOrderItem

logger = logging.getLogger(__name__)


User = get_user_model()


class WeblinkOrderItemButtonHelper(ButtonHelper):
    purchase_button_classnames = [
        "button-small",
        "icon",
        "icon-repeat",
        "purchase-button",
    ]

    def purchase_button(self, obj):
        # Define a label for our button
        return {
            "url": reverse(
                "weblink_channel:add_to_purchase_order", kwargs={"item_uuid": obj.guid},
            ),  # decide where the button links to
            "label": _("Purchase"),
            "classname": self.finalise_classname(self.purchase_button_classnames),
            "title": _("Purchase"),
            "id": obj.guid,
        }

    def get_buttons_for_obj(
        self, obj, exclude=None, classnames_add=None, classnames_exclude=None
    ):
        """
        This function is used to gather all available buttons.
        We append our custom button to the buttons list.
        """
        btns = super().get_buttons_for_obj(
            obj, exclude, classnames_add, classnames_exclude
        )
        if "purchase" not in (exclude or []):
            btns.append(self.purchase_button(obj))
        return btns


class PurchaseOrderButtonHelper(ButtonHelper):
    submit_button_classnames = [
        "button-small",
        "icon",
        "icon-repeat",
        "submit-button",
    ]
    receive_button_classnames = [
        "button-small",
        "icon",
        "icon-repeat",
        "receive-button",
    ]

    def submit_button(self, obj):
        # Define a label for our button
        return {
            "url": f"/cms/weblinkchannel/purchaseorder/submit/{obj.guid}",  # decide where the button links to
            "label": _("Submit"),
            "classname": self.finalise_classname(self.submit_button_classnames),
            "title": _("Submit"),
            "id": obj.guid,
        }

    def receive_button(self, obj):
        # Define a label for our button
        return {
            "url": f"/cms/weblink_channel/purchaseorder/receive/{obj.pk}/",  # decide where the button links to
            "label": _("Receive"),
            "classname": self.finalise_classname(self.receive_button_classnames),
            "title": _("Receive"),
            "id": obj.guid,
        }

    def get_buttons_for_obj(
        self, obj, exclude=None, classnames_add=None, classnames_exclude=None
    ):
        """
        This function is used to gather all available buttons.
        We append our custom button to the btns list.
        """
        btns = super().get_buttons_for_obj(
            obj, exclude, classnames_add, classnames_exclude
        )
        if "submit" not in (exclude or []):
            btns.append(self.submit_button(obj))
        if "receive" not in (exclude or []):
            btns.append(self.receive_button(obj))
        return btns


class PurchaseOrderURLHelper(AdminURLHelper):
    def get_action_url_pattern(self, action):
        if action in ("create", "receive", "index"):
            return self._get_action_url_pattern(action)
        return self._get_object_specific_action_url_pattern(action)

    def get_action_url_name(self, action):
        return "%s_%s_modeladmin_%s" % (
            self.opts.app_label,
            self.opts.model_name,
            action,
        )

    def get_action_url(self, action, *args, **kwargs):
        if action in ("create", "receive", "index"):
            return reverse(self.get_action_url_name(action))
        url_name = self.get_action_url_name(action)
        return reverse(url_name, args=args, kwargs=kwargs)

    @cached_property
    def receive_url(self):
        return self.get_action_url("receive")


class PurchaseOrderPermissionHelper(PermissionHelper):
    def user_can_submit_obj(self, user, obj):
        """
        Return a boolean to indicate whether `user` is permitted to submit the
        purchase order
        """
        logger.debug("Check if the user has permission to submit %s" % obj)
        perm_codename = self.get_perm_codename("receive")
        return self.user_has_specific_permission(user, perm_codename)


async def extract_metadata(web_page, link):
    data = extruct.extract(web_page)
    logger.info(f"Done processing {data}")
    return data


def extract_metadata_sync(web_page, link):
    data = extruct.extract(web_page)
    logger.info(f"Done processing {data}")
    return data


class EmailAlreadyExists(ValidationError):
    pass


@transaction.atomic
def process_weblink_checkout(**values) -> WebLinkOrder:
    customer = values.pop("customer")
    shipping = values.pop("shipping")
    items = values.pop("items")
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
        raise EmailAlreadyExists(
            message=_("Email Already Registered"), code=_("exists")
        )
    order = WebLinkOrder(
        number=get_next_value("weblink_order_number", initial_value=1000),
        customer=user,
        address=address,
        shipping_method=shipping["method"],
        weight=Weight(kg=shipping["weight"]),
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
        WebLinkOrderItem.objects.create(
            order=order,
            url=item["url"],
            name=item["name"],
            provided_price=item["price"],
            quantity=item["quantity"],
            comments=item["comments"],
            variant=variant,
        )
    return order


@transaction.atomic
def process_add_to_purchase_order(item: WebLinkOrderItem, **data) -> PurchaseOrder:
    obj = PurchaseOrder.objects.get(guid=data["purchase_order"])
    PurchaseOrderItem.objects.create(
        purchase_order=obj, sales_order_item=item, quantity=item.quantity,
    )
    other_uninit_items = item.order.items.filter(
        status=WebLinkOrderItem.StatusChoices.NEW
    ).exists()
    if not other_uninit_items:
        item.order.status = WebLinkOrder.StatusChoices.INIT
    item.status = WebLinkOrderItem.StatusChoices.INIT
    item.save()
    item.order.save()
    return obj


@transaction.atomic
def process_purchase_order(item: WebLinkOrderItem, **data) -> PurchaseOrder:
    system_supplier = data.get("system_supplier", None)
    if system_supplier:
        supplier = data["system_supplier"]
    else:
        supplier = Supplier.objects.create(name=data["supplier"])
    obj = PurchaseOrder.objects.create(
        number=get_next_value("weblink_purchase_order_number", initial_value=1000),
        sales_order=item.order,
        estimated_arrival=data["estimated_arrival"],
        supplier=supplier,
    )
    PurchaseOrderItem.objects.create(
        purchase_order=obj, sales_order_item=item, quantity=data["quantity"]
    )
    other_uninit_items = item.order.items.filter(
        status=WebLinkOrderItem.StatusChoices.NEW
    ).exists()
    if not other_uninit_items:
        item.order.status = WebLinkOrder.StatusChoices.INIT
    item.status = WebLinkOrderItem.StatusChoices.INIT
    item.save()
    item.order.save()
    return obj


@transaction.atomic
def process_receive_purchase_order_item(
    item: PurchaseOrderItem, **data
) -> PurchaseOrderItem:
    logger.debug("processing the item %s" % item.guid)
    item.received = F("received") + data["quantity"]
    if item.received == item.quantity:
        logger.info("the item is fully received")
        item.status = PurchaseOrderItem.StatusChoices.RECEIVED
    else:
        logger.info("the item is partially received")
        item.status = PurchaseOrderItem.StatusChoices.PARTIAL
    item.save()
    logger.info("processing receive completed")
    return item


@transaction.atomic
def submit_order_for_purchase(instance: PurchaseOrder) -> PurchaseOrder:
    instance.status = PurchaseOrder.StatusChoices.SENT
    PurchaseOrderItem.objects.select_for_update().filter(
        purchase_order=instance
    ).update(status=PurchaseOrderItem.StatusChoices.SENT)
    instance.save()
    instance.refresh_from_db()
    return instance
