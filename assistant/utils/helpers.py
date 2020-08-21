import logging
import unicodedata

import requests
from django.contrib.auth.models import User
from django.db.models import CharField, Value
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def generate_username(full_name):

    """
    >>> from utils import generate_username
    >>> from django.contrib.auth.models import User
    >>>
    >>> name = 'Sebastião Henrique de Almeida Gonçalves'
    >>> username = generate_username(name)
    >>> print username
    sgoncalves
    >>> u = User(username=username, password="123456", email="teste1@fundacaoaprender.org.br")
    >>> u.save()
    >>>
    >>> username = generate_username(name)
    >>> print username
    sebastiaog
    >>> u = User(username=username, password="123456", email="teste2@fundacaoaprender.org.br")
    >>> u.save()
    >>>
    >>> username = generate_username(name)
    >>> print username
    sebastiao1
    >>> u = User(username=username, password="123456", email="teste3@fundacaoaprender.org.br")
    >>> u.save()
    >>>
    >>> username = generate_username(name)
    >>> print username
    sebastiao2
    >>> u = User(username=username, password="123456", email="teste4@fundacaoaprender.org.br")
    >>> u.save()
    >>>
    >>> username = generate_username(name)
    >>> print username
    sebastiao3
    >>> u = User(username=username, password="123456", email="teste5@fundacaoaprender.org.br")
    >>> u.save()
    """

    name = unicodedata.normalize("NFKD", unicode(full_name.lower())).encode(
        "ASCII", "ignore"
    )
    name = name.split(" ")
    lastname = name[-1]
    firstname = name[0]

    username = "%s%s" % (firstname[0], lastname)
    if User.objects.filter(username=username).count() > 0:
        username = "%s%s" % (firstname, lastname[0])
        if User.objects.filter(username=username).count() > 0:
            users = (
                User.objects.filter(username__regex=r"^%s[1-9]{1,}$" % firstname)
                .order_by("username")
                .values("username")
            )
            if len(users) > 0:
                last_number_used = map(
                    lambda x: int(x["username"].replace(firstname, "")), users
                )
                last_number_used.sort()
                last_number_used = last_number_used[-1]
                number = last_number_used + 1
                username = "%s%s" % (firstname, number)
            else:
                username = "%s%s" % (firstname, 1)

    return username


def combined_recent(limit, **kwargs):
    """A helper function to combain multiple queryset from different models.

    Example:
        >>> recent = combined_recent(
        >>>    20,
        >>>    entry=Entry.objects.all(),
        >>>    photo=Photo.objects.all(),
        >>> )
    """
    datetime_field = kwargs.pop("datetime_field", "created")
    querysets = []
    for key, queryset in kwargs.items():
        querysets.append(
            queryset.annotate(
                recent_changes_type=Value(key, output_field=CharField())
            ).values("pk", "recent_changes_type", datetime_field)
        )
    union_qs = querysets[0].union(*querysets[1:])
    records = []
    for row in union_qs.order_by("-{}".format(datetime_field))[:limit]:
        records.append(
            {
                "type": row["recent_changes_type"],
                "when": row[datetime_field],
                "pk": row["pk"],
            }
        )
    # Now we bulk-load each object type in turn
    to_load = {}
    for record in records:
        to_load.setdefault(record["type"], []).append(record["pk"])
    fetched = {}
    for key, pks in to_load.items():
        for item in kwargs[key].filter(pk__in=pks):
            fetched[(key, item.pk)] = item
    # Annotate 'records' with loaded objects
    for record in records:
        record["object"] = fetched[(record["type"], record["pk"])]
    return records


# class TimeoutHTTPAdapter(HttpAdapter):
#     DEFAULT_TIMEOUT = 5

#     def __init__(self, *args, **kwargs):
#         self.timeout = self.DEFAULT_TIMEOUT
#         if "timeout" in kwargs:
#             self.timeout = kwargs["timeout"]
#             del kwargs["timeout"]
#         super().__init__(*args, **kwargs)

#     def send(self, request, **kwargs):
#         timeout = kwargs.get("timeout")
#         if timeout is None:
#             kwargs["timeout"] = self.timeout
#         return super().send(request, **kwargs)


# def logging_hook(response, *args, **kwargs):
#     data = dump.dump_all(response)
#     logger.info(data.decode("utf-8"))


# retry_strategy = Retry(
#     total=3,
#     status_forcelist=[429, 500, 502, 503, 504],
#     method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
#     backoff_factor=1,
# )
# adapter = TimeoutHTTPAdapter(timeout=2.5, max_retries=retry_strategy)

# http = requests.Session()
# http.hooks["response"] = [logging_hook]
# http.mount("https://", adapter)
# http.mount("http://", adapter)
