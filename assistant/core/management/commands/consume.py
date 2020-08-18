from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand

from assistant.core.pub_sub import Consumer


class Command(BaseCommand):
    """A management command to run a worker to consume events from rabbitmq."""

    help = _("Consumes messages from RabbitMQ")

    callback_functions = {'update_user': 'update_user'}

    def add_arguments(self, parser):
        parser.add_argument(
            'exchange',
            nargs='+',
            type=str,
            help=_("The exchange to consume from."),
        )
        parser.add_argument(
            'queue', nargs='+', type=str, help=_("The queue to consume from.")
        )
        parser.add_argument(
            'routing_key',
            nargs='+',
            type=str,
            help=_("The routing key to consume from."),
        )
        # parser.add_argument('action', nargs='+', type=str, help=_("The callback function key in the dictionary."))

    def _callback(self, channel, method, properties, body):
        self.stdout.write(
            self.style.SUCCESS(f"{channel} - {method} - {properties} - {body}")
        )

    def _onerror_callback(self, error):
        self.stdout.write(self.style.ERROR(f"{error}"))

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f"{options['exchange'][0]}"))
        self.stdout.write(self.style.SUCCESS(f"{options['queue'][0]}"))
        self.stdout.write(self.style.SUCCESS(f"{options['routing_key'][0]}"))
        consumer = Consumer(
            exchange_name=options['exchange'],
            queue_name=options['queue'],
            routing_key=options['routing_key'],
            callback=self._callback,
            error_callback=self._onerror_callback,
        )
        consumer.start()
