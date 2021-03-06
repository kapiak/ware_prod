import json
import logging
from functools import wraps

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

from .helpers import domain_is_valid, hmac_is_valid, proxy_signature_is_valid

logger = logging.getLogger(__name__)


class HttpResponseMethodNotAllowed(HttpResponse):
    status_code = 405


def webhook(f):
    """
    A view decorator that checks and validates a Shopify Webhook request.
    """

    @wraps(f)
    def wrapper(request, *args, **kwargs):
        # Ensure the request is a POST request.
        if request.method != 'POST':
            logger.info("Only POST request is allowed.")
            return HttpResponseMethodNotAllowed()
        
        # Try to get required headers and decode the body of the request.
        try:
            topic = request.META['HTTP_X_SHOPIFY_TOPIC']
            domain = request.META['HTTP_X_SHOPIFY_SHOP_DOMAIN']
            hmac = request.META['HTTP_X_SHOPIFY_HMAC_SHA256'] if 'HTTP_X_SHOPIFY_HMAC_SHA256' in request.META else None
            data = json.loads(request.body.decode('utf-8'))
        except (KeyError, ValueError) as e:
            logger.info("The webhook request missing META. Raised: %s", e)
            return HttpResponseBadRequest()

        # Verify the domain.
        if not domain_is_valid(domain):
            logger.info("Invalid domain.")
            return HttpResponseBadRequest()

        # Verify the HMAC.
        if not hmac_is_valid(request.body, settings.SHOPIFY_WEBHOOK_SECRET, hmac):
            logger.info("Invalid hmac.")
            return HttpResponseForbidden()

        # Otherwise, set properties on the request object and return.
        request.webhook_topic = topic
        request.webhook_data = data
        request.webhook_domain = domain
        return f(request, *args, **kwargs)

    return wrapper


def carrier_request(f):
    """
    A view decorator that checks and validates a CarrierService request from Shopify.
    """

    @wraps(f)
    def wrapper(request, *args, **kwargs):
        # Ensure the request is a POST request.
        if request.method != 'POST':
            logger.info("Only POST request is allowed.")
            return HttpResponseMethodNotAllowed()

        # Try to get required headers and decode the body of the request.
        try:
            domain = request.META['HTTP_X_SHOPIFY_SHOP_DOMAIN']
            hmac = request.META['HTTP_X_SHOPIFY_HMAC_SHA256'] if 'HTTP_X_SHOPIFY_HMAC_SHA256' in request.META else None
            data = json.loads(request.body)
        except (KeyError, ValueError) as e:
            logger.info("The webhook request missing META. Raised: %s", e)
            return HttpResponseBadRequest()

        # Verify the domain.
        if not domain_is_valid(domain):
            logger.info("Invalid domain.")
            return HttpResponseBadRequest()

        # Verify the HMAC.
        if not hmac_is_valid(request.body, settings.SHOPIFY_WEBHOOK_SECRET, hmac):
            logger.info("Invalid hmac.")
            return HttpResponseForbidden()

        # Otherwise, set properties on the request object and return.
        request.carrier_request_data = data
        request.carrier_request_domain = domain
        return f(request, *args, **kwargs)

    return wrapper


def app_proxy(f):
    """
    A view decorator that checks and validates a Shopify Application proxy request.
    """

    @wraps(f)
    def wrapper(request, *args, **kwargs):

        # Verify the signature.
        if not proxy_signature_is_valid(request, settings.SHOPIFY_WEBHOOK_SECRET):
            logger.info("Signature mismatch.")
            return HttpResponseBadRequest()

        return f(request, *args, **kwargs)

    return wrapper
