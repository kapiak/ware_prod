from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from wagtail.contrib.modeladmin.helpers import ButtonHelper


class ProductButtonHelper(ButtonHelper):

    # Define classes for our button, here we can set an icon for example
    orders_button_classnames = [
        "button-small",
        "icon",
        "icon-list-ul",
        "orders-button",
    ]
    purchase_button_classnames = ["button-small", "icon", "icon-repeat"]
    allocate_button_classnames = [
        "button-small",
        "icon",
        "icon-link",
        "purchase-button",
    ]

    def orders_button(self, obj):
        # Define a label for our button
        return {
            "url": reverse(
                "products:product_orders_modal_workflow", kwargs={"guid": obj.guid},
            ),  # decide where the button links to
            "label": _("Orders"),
            "classname": self.finalise_classname(self.orders_button_classnames),
            "title": _("Orders"),
            "id": obj.guid,
        }

    def purchase_button(self, obj):
        # Define a label for our button
        return {
            "url": reverse(
                "products:make_product_purchase", kwargs={"guid": obj.guid}
            ),  # decide where the button links to
            "label": _("Purchase"),
            "classname": self.finalise_classname(self.purchase_button_classnames),
            "title": _("Purchase"),
            "id": obj.guid,
        }

    def allocate_button(self, obj):
        # Define a label for our button
        return {
            "url": "/",  # decide where the button links to
            "label": _("Allocate"),
            "classname": self.finalise_classname(self.allocate_button_classnames),
            "title": _("Allocate"),
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
        if "orders" not in (exclude or []):
            btns.append(self.orders_button(obj))
        if "purchase" not in (exclude or []):
            btns.append(self.purchase_button(obj))
        if "allocate" not in (exclude or []):
            btns.append(self.allocate_button(obj))
        return btns


class ProductVariantButtonHelper(ButtonHelper):

    allocate_button_classnames = [
        "button-small",
        "icon",
        "icon-link",
        "allocate-button",
    ]
    purchase_button_classnames = [
        "button-small",
        "icon",
        "icon-repeat",
        "purchase-button",
    ]
    receive_button_classnames = [
        "button-small",
        "icon",
        "icon-repeat",
        "receive-button",
    ]

    def purchase_button(self, obj):
        # Define a label for our button
        return {
            "url": reverse(
                "products:make_product_purchase", kwargs={"guid": obj.guid}
            ),  # decide where the button links to
            "label": _("Purchase"),
            "classname": self.finalise_classname(self.purchase_button_classnames),
            "title": _("Purchase"),
            "id": obj.guid,
        }

    def allocate_button(self, obj):
        # Define a label for our button
        return {
            "url": reverse(
                "products:allocate_product_to_order",
                kwargs={"guid": obj.guid},  # decide where the button links to
            ),
            "label": _("Allocate"),
            "classname": self.finalise_classname(self.allocate_button_classnames),
            "title": _("Allocate"),
            "id": obj.guid,
        }

    def receive_button(self, obj):
        # Define a label for our button
        return {
            "url": reverse(
                "products:receive_product_stock",
                kwargs={"guid": obj.guid},  # decide where the button links to
            ),
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
        if "purchase" not in (exclude or []):
            btns.append(self.purchase_button(obj))
        if "receive" not in (exclude or []):
            btns.append(self.receive_button(obj))
        if "allocate" not in (exclude or []):
            btns.append(self.allocate_button(obj))

        return btns
