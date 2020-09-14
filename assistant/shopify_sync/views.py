import logging
from datetime import datetime
from typing import Dict, List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, View
from pydantic import BaseModel

from . import signals
from .decorators import webhook
from .helpers import get_signal_name_for_topic
from .models import EventStore

logger = logging.getLogger(__name__)


class StreamListView(LoginRequiredMixin, ListView):
    template_name = "shopify_sync/stream.html"
    queryset = EventStore.objects.all()
    context_object_name = "events"



class WebhookView(View):
    """
    A view to be used as the endpoint for webhook requests from Shopify.
    Accepts only the POST method and utilises the @webhook view decorator to validate the request.
    """

    @method_decorator(csrf_exempt)
    @method_decorator(webhook)
    def dispatch(self, request, *args, **kwargs):
        """
        The dispatch() method simply calls the parent dispatch method, but is required as method decorators need to be
        applied to the dispatch() method rather than to individual HTTP verb methods (eg post()).
        """
        logger.info("Incoming webhook from shopify")
        return super(WebhookView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Receive a webhook POST request.
        """

        # Convert the topic to a signal name and trigger it.
        signal_name = get_signal_name_for_topic(request.webhook_topic)
        logger.info("Incoming %s webhook from shopify", signal_name)
        try:
            signals.webhook_received.send_robust(self, domain=request.webhook_domain, topic=request.webhook_topic, data=request.webhook_data)
            logger.info("Incoming webhook Signal Fired. Domain: %s, Topic: %s", request.webhook_domain, request.webhook_topic)
            try:
                event = EventStore.objects.create(domain=request.webhook_domain, topic=request.webhook_topic, data=request.webhook_data)
                getattr(signals, signal_name).send_robust(self, event=event, domain=request.webhook_domain, topic=request.webhook_topic, data=request.webhook_data)
                logger.info("Signal %s fired", getattr(signals, signal_name))
            except Exception as e:
                logger.info("Couldn't Store Event Data. %s", e)
        except AttributeError as e:
            logger.exception("Exception firing the webhook %s. Raised: %s", getattr(signals, signal_name), e)
            return HttpResponseBadRequest()
        logger.info("All good with the webhook. returning 200")
        # All good, return a 200.
        return HttpResponse('OK')
