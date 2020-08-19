from django.apps import AppConfig


class WeblinkChannelConfig(AppConfig):
    name = "assistant.weblink_channel"

    def ready(self):
        try:
            import assistant.weblink_channel.receivers  # noqa F401
        except ImportError:
            pass
