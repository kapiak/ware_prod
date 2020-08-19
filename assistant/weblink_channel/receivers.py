import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from assistant.orders.models import Order
from .models import WebLinkOrder

logger = logging.getLogger(__name__)
