import logging

from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from wagtail.contrib.modeladmin.helpers import (
    AdminURLHelper,
    ButtonHelper,
    PermissionHelper,
)

logger = logging.getLogger(__name__)


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
            "classname": self.finalise_classname(self.submit_button_classnames),
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
        if action in ("create", "submit", "index"):
            return self._get_action_url_pattern(action)
        return self._get_object_specific_action_url_pattern(action)

    def get_action_url_name(self, action):
        return "%s_%s_modeladmin_%s" % (
            self.opts.app_label,
            self.opts.model_name,
            action,
        )

    def get_action_url(self, action, *args, **kwargs):
        if action in ("create", "submit", "index"):
            return reverse(self.get_action_url_name(action))
        url_name = self.get_action_url_name(action)
        return reverse(url_name, args=args, kwargs=kwargs)

    @cached_property
    def submit_url(self):
        return self.get_action_url("submit")


class PurchaseOrderPermissionHelper(PermissionHelper):
    def user_can_submit_obj(self, user, obj):
        """
        Return a boolean to indicate whether `user` is permitted to submit the
        purchase order
        """
        logger.debug("Check if the user has permission to submit %s" % obj)
        perm_codename = self.get_perm_codename("submit")
        return self.user_has_specific_permission(user, perm_codename)
