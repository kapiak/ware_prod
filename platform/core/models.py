import uuid
import json
from typing import Dict, Union

import requests

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampMixin(models.Model):
    """Abstract model which provides a timestamp for the creation, and the updates on an Object."""

    created_at = models.DateTimeField(verbose_name=_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("Updated at"), auto_now=True)

    class Meta:
        abstract = True


class AuditMixin(models.Model):
    """Abstract model which provides an audit for the creation, and the updates on an Object."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_%(app_label)s_%(class)s",
        null=True,
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_%(app_label)s_%(class)s",
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True


class GUIDMixin(models.Model):
    """Abstract model for a uuid."""

    guid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(GUIDMixin, AuditMixin, TimestampMixin):
    """Abstract model as the base for all models."""

    class Meta:
        abstract = True


class RemoteModel:
    service_base_url: str = ''

    def __init__(self, request: HttpRequest, entity: str, version: str) -> None:
        self.request = request
        self.entity = entity
        self.version = version
        self.url = f"{self.service_base_url}/{self.version}/{self.entity}/"

    def _header(self, kwargs: Union[Dict, None] = None) -> Dict:
        base_headers = {'content-type': 'application/json'}
        override_headers = kwargs or {}
        return {
            **request.META,
            **base_headers,
            **override_headers,
        }

    def _cookies(self, kwargs: Union[Dict, None] = None) -> Dict:
        override_cookies = kwargs or {}
        return {
            **self.request.COOKIES,
            **override_cookies,
        }

    def get(self, entity_id: Union[int, uuid.UUID]):
        response = requests.get(
            f'{self.url}/{entity_id}', 
            headers=self._headers(), 
            cookies=self._cookies()
        )
        return response

    def filter(self, **params: Dict = None):
        params = f"?{urllib.parse.urlencode(conditions)}" if conditions else ""
        response = requests.get(
            f'{self.url}/{params}',
            headers=self._headers(),
            cookies=self._cookies()
        )
        return response

    def delete(self, entity_id: Union[int, uuid.UUID]):
        response = requests.delete(
            f'{self.url}/{entity_id}',
            headers=self._headers(),
            cookies=self._cookies()
        )
        return response

    def create(self, entity_id: Union[int, uuid.UUID], entity_data: Dict):
        response = requests.post(
            f'{self.url}/',
            data=json.dumps(entity_data),
            headers=self._headers(),
            cookies=self._cookies()
        )
        return response

    def update(self, entity_id: Union[int, uuid.UUID], entity_data: Dict):
        data = json.dumps(entity_data)
        response = requests.put(
            f'{self.url}/{entity_id}'
            data=data,
            headers=self._headers(),
            cookies=self._cookies()
        )
        return response