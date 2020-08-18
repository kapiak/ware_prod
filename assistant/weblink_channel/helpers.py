import logging
import random
import string

import extruct
from measurement.measures import Weight

from django.urls import reverse
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from sequences import get_next_value

from assistant.addresses.models import Address
from assistant.products.models import Supplier
from .models import (
    WebLinkOrder,
    WebLinkOrderItem,
    PurchaseOrder,
    PurchaseOrderItem,
)

from wagtail.contrib.modeladmin.helpers import ButtonHelper, AdminURLHelper

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
                "weblink_channel:add_to_purchase_order",
                kwargs={'item_uuid': obj.guid},
            ),  # decide where the button links to
            "label": _("Purchase"),
            "classname": self.finalise_classname(
                self.purchase_button_classnames
            ),
            "title": _("Purchase"),
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

    def submit_button(self, obj):
        # Define a label for our button
        return {
            "url": "",  # decide where the button links to
            "label": _("Submit"),
            "classname": self.finalise_classname(
                self.submit_button_classnames
            ),
            "title": _("Submit"),
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
        if "submit_button" not in (exclude or []):
            btns.append(self.submit_button(obj))
        return btns


class PurchaseOrderURLHelper(AdminURLHelper):
    def get_action_url_pattern(self, action):
        if action in ('create', 'submit', 'index'):
            return self._get_action_url_pattern(action)
        return self._get_object_specific_action_url_pattern(action)

    def get_action_url_name(self, action):
        return '%s_%s_modeladmin_%s' % (
            self.opts.app_label,
            self.opts.model_name,
            action,
        )

    def get_action_url(self, action, *args, **kwargs):
        if action in ('create', 'submit', 'index'):
            return reverse(self.get_action_url_name(action))
        url_name = self.get_action_url_name(action)
        return reverse(url_name, args=args, kwargs=kwargs)

    @cached_property
    def submit_url(self):
        return self.get_action_url('submit')


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
    customer = values.pop('customer')
    shipping = values.pop('shipping')
    items = values.pop('items')
    address = Address.objects.create(
        first_name=customer['name'],
        city=customer['city'],
        city_area=customer['state'],
        country=customer['country'],
        postal_code=customer['code'],
    )
    username = slugify(customer['name'])
    if User.objects.filter(username=username).exists():
        random_string = ''.join(
            [
                random.choice(string.ascii_letters + string.digits)
                for n in range(5)
            ]
        )
        username = username + random_string
    if not User.objects.filter(email=customer['email']):
        user = User.objects.create_user(
            name=customer['name'],
            username=slugify(username),
            email=customer['email'],
            password=customer['password'],
            shipping_address=address,
        )
    else:
        raise EmailAlreadyExists(
            message=_("Email Already Registered"), code=_("exists")
        )
    order = WebLinkOrder.objects.create(
        number=get_next_value("weblink_order_number", initial_value=1000),
        customer=user,
        address=address,
        shipping_method=shipping['method'],
        weight=Weight(kg=shipping['weight']),
    )
    for item in items:
        WebLinkOrderItem.objects.create(
            order=order,
            url=item['url'],
            name=item['name'],
            provided_price=item['price'],
            quantity=item['quantity'],
            comments=item['comments'],
        )
    return order


@transaction.atomic
def process_add_to_purchase_order(
    item: WebLinkOrderItem, **data
) -> PurchaseOrder:
    obj = PurchaseOrder.objects.get(guid=data['purchase_order'])
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
    system_supplier = data.get('system_supplier', None)
    if system_supplier:
        supplier = data['system_supplier']
    else:
        supplier = Supplier.objects.create(name=data['supplier'])
    obj = PurchaseOrder.objects.create(
        number=get_next_value(
            "weblink_purchase_order_number", initial_value=1000
        ),
        sales_order=item.order,
        estimated_arrival=data['estimated_arrival'],
        supplier=supplier,
    )
    PurchaseOrderItem.objects.create(
        purchase_order=obj, sales_order_item=item, quantity=data['quantity']
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
