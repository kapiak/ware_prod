from django.apps import AppConfig


class WarehouseConfig(AppConfig):
    name = "assistant.warehouse"

    def ready(self):
        try:
            import assistant.warehouse.signal_handlers  # noqa F401
        except ImportError:
            pass