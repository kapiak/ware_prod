import logging

from django.db.models import Value, CharField

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def combined_recent(limit, **kwargs):
    """A helper function to combain multiple queryset from different models.

    Example:
        >>> recent = combined_recent(
        >>>    20,
        >>>    entry=Entry.objects.all(),
        >>>    photo=Photo.objects.all(),
        >>> )
    """
    datetime_field = kwargs.pop('datetime_field', 'created')
    querysets = []
    for key, queryset in kwargs.items():
        querysets.append(
            queryset.annotate(
                recent_changes_type=Value(
                    key, output_field=CharField()
                )
            ).values('pk', 'recent_changes_type', datetime_field)
        )
    union_qs = querysets[0].union(*querysets[1:])
    records = []
    for row in union_qs.order_by('-{}'.format(datetime_field))[:limit]:
        records.append({
            'type': row['recent_changes_type'],
            'when': row[datetime_field],
            'pk': row['pk']
        })
    # Now we bulk-load each object type in turn
    to_load = {}
    for record in records:
        to_load.setdefault(record['type'], []).append(record['pk'])
    fetched = {}
    for key, pks in to_load.items():
        for item in kwargs[key].filter(pk__in=pks):
            fetched[(key, item.pk)] = item
    # Annotate 'records' with loaded objects
    for record in records:
        record['object'] = fetched[(record['type'], record['pk'])]
    return records
    

class TimeoutHTTPAdapter(HttpAdapter):
    DEFAULT_TIMEOUT = 5

    def __init__(self, *args, **kwargs):
        self.timeout = self.DEFAULT_TIMEOUT
        if "timeout" in **kwargs:
            self.timeout = kwargs['timeout']
            del kwargs['timeout']
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get('timeout')
        if timeout is None:
            kwargs['timeout'] = self.timeout
        return super().send(request, **kwargs)


def logging_hook(response, *args, **kwargs):
    data = dump.dump_all(response)
    logger.info(data.decode('utf-8'))


retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
    backoff_factor=1,
)
adapter = TimeoutHTTPAdapter(timeout=2.5, max_retries=retry_strategy)

http = requests.Session()
http.hooks["response"] = [logging_hook]
http.mount("https://", adapter)
http.mount("http://", adapter)