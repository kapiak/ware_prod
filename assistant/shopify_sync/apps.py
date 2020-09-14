from django.apps import AppConfig


class ShopifySyncConfig(AppConfig):
    name = 'assistant.shopify_sync'

    def ready(self):
        try:
            import assistant.shopify_sync.signal_handlers  # noqa F401
        except ImportError:
            pass
