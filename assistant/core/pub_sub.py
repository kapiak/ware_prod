import json
import os
import threading
import time
import logging
from typing import Callable

from django.conf import settings

from pika import (
    BasicProperties,
    BlockingConnection,
    PlainCredentials,
    ConnectionParameters,
)
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError, AMQPChannelError, StreamLostError, ChannelClosedByBroker
from pika.spec import PERSISTENT_DELIVERY_MODE
from threading import Thread

CONNECTION_ERRORS = (AMQPConnectionError, ConnectionResetError, StreamLostError, ChannelClosedByBroker)
CHANNEL_ERROR = AMQPChannelError

logger = logging.getLogger(__name__)


class Publisher(object):
    """
    This class offers a ``BlockingConnection`` from pika that automatically handles
    queue declares and bindings plus retry logic built for its connection and publishing.
    """

    def __init__(self, exchange_name: str, queue_name: str, routing_key: str, **kwargs):
        """
        :param exchange_name: Your exchange name.
        :param queue_name: Your queue name.
        :param routing_key: Your queue name.
        :keyword host: Your RabbitMQ host. Checks env var ``RABBITMQ_HOST``. Default: ``"localhost"``
        :keyword port: Your RabbitMQ port. Checks env var ``RABBITMQ_PORT``. Default: ``5672``
        :keyword username: Your RabbitMQ username. Default: ``"guest"``
        :keyword password: Your RabbitMQ password. Default: ``"guest"``
        :keyword connection_attempts: How many times should PyRMQ try?. Default: ``3``
        :keyword retry_delay: Seconds between retries.. Default: ``5``
        :keyword error_callback: Callback function to be called when connection_attempts is reached.
        :keyword infinite_retry: Tells PyRMQ to keep on retrying to publish while firing error_callback, if any. Default: ``False``
        """

        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.host = settings.RABBITMQ_HOST
        self.port = settings.RABBITMQ_PORT
        self.username = settings.RABBITMQ_USER
        self.password = settings.RABBITMQ_PASSWORD
        self.connection_attempts = kwargs.get("connection_attempts") or 3
        self.retry_delay = kwargs.get("retry_delay") or 5
        self.retry_backoff_base = kwargs.get("retry_backoff_base") or 2
        self.retry_backoff_constant_secs = (
            kwargs.get("retry_backoff_constant_secs") or 5
        )
        self.error_callback = kwargs.get("error_callback")
        self.infinite_retry = kwargs.get("infinite_retry") or False

        self.connection_parameters = ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=PlainCredentials(self.username, self.password),
            connection_attempts=self.connection_attempts,
            retry_delay=self.retry_delay,
        )

        self.connections = {}
        self.channels = {}

    def __send_reconnection_error_message(self, retry_count, error) -> None:
        """
        Send error message to your preferred location.
        :param retry_count: Amount retries the Publisher tried before sending an error message.
        :param error: Error that prevented the Publisher from sending the message.
        """
        message = (
            f"Service tried to reconnect to queue **{retry_count}** times "
            f"but still failed."
            f"\n{repr(error)}"
        )
        logger.exception(error)

        if self.error_callback:
            self.error_callback(message)

    def __create_connection(self) -> BlockingConnection:
        """
        Creates pika's ``BlockingConnection`` from the given connection parameters.
        """
        return BlockingConnection(self.connection_parameters)

    def declare_queue(self, channel) -> None:
        """
        Declare and a bind a channel to a queue.
        :param channel: pika Channel
        """
        channel.exchange_declare(exchange=self.exchange_name, durable=True)
        channel.queue_declare(queue=self.queue_name, durable=True)
        channel.queue_bind(
            queue=self.queue_name,
            exchange=self.exchange_name,
            routing_key=self.routing_key,
        )
        channel.confirm_delivery()

    def connect(self, retry_count=1) -> (BlockingConnection, BlockingChannel):
        """
        Creates pika's ``BlockingConnection`` and initializes queue bindings.
        :param retry_count: Amount retries the Publisher tried before sending an error message.
        """
        try:
            connection = self.__create_connection()
            channel = connection.channel()

            self.declare_queue(channel)

            return connection, channel

        except CONNECTION_ERRORS as error:
            self.__send_reconnection_error_message(
                self.connection_attempts * retry_count, error
            )
            if not self.infinite_retry:
                raise error

            time.sleep(self.retry_delay)

            return self.connect(retry_count=(retry_count + 1))

    def publish(self, data: dict, attempt=0, retry_count=1) -> None:
        """
        Publishes data to RabbitMQ.
        :param data: Data to be published.
        :param attempt: Number of attempts made.
        :param retry_count: Amount retries the Publisher tried before sending an error message.
        """
        worker_id = os.getpid()
        ident = f"{worker_id}-{threading.currentThread().ident}"

        if worker_id not in self.connections:
            connection, channel = self.connect()
            self.connections[worker_id] = connection
            self.channels[ident] = channel

        if ident not in self.channels:
            channel = self.connections[worker_id].channel()
            self.declare_queue(channel)
            self.channels[ident] = channel

        channel = self.channels[ident]

        try:
            basic_properties_kwargs = {
                "delivery_mode": PERSISTENT_DELIVERY_MODE,
            }

            channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key,
                body=json.dumps(data),
                properties=BasicProperties(**basic_properties_kwargs),
                mandatory=True,
            )
            logger.info("Published Event")

        except CONNECTION_ERRORS as error:
            if not (retry_count % self.connection_attempts):
                self.__send_reconnection_error_message(retry_count, error)
                if not self.infinite_retry:
                    raise error

            time.sleep(self.retry_delay)

            connection, channel = self.connect()
            self.connections[worker_id] = connection
            self.channels[ident] = channel

            self.publish(data, attempt=attempt, retry_count=(retry_count + 1))

        except CHANNEL_ERROR as error:
            if not (retry_count % self.connection_attempts):
                self.__send_reconnection_error_message(retry_count, error)
                if not self.infinite_retry:
                    raise error

            time.sleep(self.retry_delay)
            self.publish(data, attempt=attempt, retry_count=(retry_count + 1))


class Consumer(object):
    """
    This class uses a ``BlockingConnection`` from pika that automatically handles
    queue declares and bindings plus retry logic built for its connection and consumption.
    It starts its own thread upon initialization and runs pika's ``start_consuming()``.
    """

    def __init__(
        self,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        callback: Callable,
        **kwargs,
    ):
        """
        :param exchange_name: Your exchange name.
        :param queue_name: Your queue name.
        :param routing_key: Your queue name.
        :param callback: Your callback that should handle a consumed message
        :keyword host: Your RabbitMQ host. Default: ``"localhost"``
        :keyword port: Your RabbitMQ port. Default: ``5672``
        :keyword username: Your RabbitMQ username. Default: ``"guest"``
        :keyword password: Your RabbitMQ password. Default: ``"guest"``
        :keyword connection_attempts: How many times should PyRMQ try? Default: ``3``
        :keyword retry_delay: Seconds between retries.. Default: ``5``
        :keyword retry_backoff_base: Exponential backoff base in seconds. Default: ``2``
        :keyword retry_backoff_constant_secs: Exponential backoff constant in seconds. Default: ``5``
        """
        self.connection = None
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.message_received_callback = callback
        self.host = settings.RABBITMQ_HOST
        self.port = settings.RABBITMQ_PORT
        self.username = settings.RABBITMQ_USER
        self.password = settings.RABBITMQ_PASSWORD
        self.connection_attempts = kwargs.get("connection_attempts") or 3
        self.retry_delay = kwargs.get("retry_delay") or 5
        self.error_callback = kwargs.get("error_callback")
        self.infinite_retry = kwargs.get("infinite_retry") or False
        self.channel = None
        self.thread = None

        self.connection_parameters = ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=PlainCredentials(self.username, self.username),
            connection_attempts=self.connection_attempts,
            retry_delay=self.retry_delay,
        )

    def start(self):
        self.connect()
        
        self.thread = Thread(target=self.consume)
        self.thread.setDaemon(True)
        self.thread.start()

    def __send_reconnection_error_message(self, retry_count, error) -> None:
        """
        Send error message to your preferred location.
        :param retry_count: Amount retries the Publisher tried before sending an error message.
        :param error: Error that prevented the Publisher from sending the message.
        """
        message = (
            f"Service tried to reconnect to queue **{retry_count}** times "
            f"but still failed."
            f"\n{repr(error)}"
        )
        if self.error_callback:
            self.error_callback(message)

        logger.exception(error)

    def __create_connection(self) -> BlockingConnection:
        """
        Creates a pika BlockingConnection from the given connection parameters.
        """
        return BlockingConnection(self.connection_parameters)

    def _consume_message(self, channel, method, properties, data) -> None:
        """
        Wraps the user provided callback and gracefully handles its errors and
        calling pika's ``basic_ack`` once successful.
        :param channel: pika's Channel this message was received.
        :param method: pika's basic Return
        :param properties: pika's BasicProperties
        :param data: Data received in bytes.
        """

        if isinstance(data, bytes):
            data = data.decode("ascii")

        data = json.loads(data)

        try:
            logger.debug("Received message from queue")

            self.message_received_callback(data)

        except Exception as error:
            logger.exception(error)

        channel.basic_ack(delivery_tag=method.delivery_tag)

    def connect(self, retry_count=1) -> None:
        """
        Creates a BlockingConnection from pika and initializes queue bindings.
        :param retry_count: Amount retries the Publisher tried before sending an error message.
        """
        try:
            self.connection = self.__create_connection()
            self.channel = self.connection.channel()
            logger.info("Establied Connection.")
        except CONNECTION_ERRORS as error:
            self.__send_reconnection_error_message(
                self.connection_attempts * retry_count, error
            )
            if not self.infinite_retry:
                raise error

            time.sleep(self.retry_delay)

            self.connect(retry_count=(retry_count + 1))

    def close(self) -> None:
        """
        Manually closes a connection to RabbitMQ. Useful for debugging and tests.
        """
        self.thread.join(0.1)

    def consume(self, retry_count=1) -> None:
        """
        Wraps pika's ``basic_consume()`` and ``start_consuming()`` with retry logic.
        """
        try:
            self.channel.basic_consume(self.queue_name, self._consume_message)

            self.channel.start_consuming()

        except CONNECTION_ERRORS as error:
            if not (retry_count % self.connection_attempts):
                self.__send_reconnection_error_message(retry_count, error)
                if not self.infinite_retry:
                    raise error

            time.sleep(self.retry_delay)

            self.connect()
            self.consume(retry_count=(retry_count + 1))


""" EXAMPLE Publisher

def error_callback(error):
    logger.error(f"Error in the publisher: {error}")

publisher = Publisher(
    exchange_name="incorrect_exchange_name",
    queue_name="incorrect_queue_name",
    routing_key="incorrect_routing_key",
    username="incorrect_username",  # BlockingConnection class from pika goes on an infinite loop if credentials are wrong.
    error_callback=error_callback,
    infinite_retry=True,
)

body = {"sample_body": "value"}

publisher.publish(body)
"""

""" Example Consumer

def callback(data):
    logger.info(f"Received {data}!")

consumer = Consumer(
    exchange_name="exchange_name",
    queue_name="queue_name",
    routing_key="routing_key",
    callback=callback
)

consumer.start()
"""