from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    name = "platform.core"
    verbose_name = _("Core")

    def ready(self):
        try:
            import platform.core.signals  # noqa F401
        except ImportError:
            pass