from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from assistant.core.models import BaseModel


class User(AbstractUser):
    """Default user for assistant.
    """

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)

    shipping_address = models.ForeignKey(
        "addresses.Address",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    billing_address = models.ForeignKey(
        "addresses.Address",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    @property
    def fullname(self):
        return self.name or self.email

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
