import json

from django.contrib import admin
from django.db.models import JSONField
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from assistant.core.admin import PrettyJSONWidget

from .models import ErrorSyncLog, EventStore, ShopifySyncLog


class ShopifySyncLogAdmin(admin.ModelAdmin):
    pass


admin.site.register(ShopifySyncLog, ShopifySyncLogAdmin)



class ErrorSyncLogAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }


admin.site.register(ErrorSyncLog, ErrorSyncLogAdmin)


class EventStoreAdmin(admin.ModelAdmin):
    list_display = ("topic", "domain", "status", "created_at", "updated_at", "data_prettified")
    list_filter = ("topic",)

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }

    def data_prettified(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.data, sort_keys=True, indent=2)

        # Truncate the data. Alter as needed
        response = response[:5000]

        # Get the Pygments formatter
        formatter = HtmlFormatter(style='colorful')

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    data_prettified.short_description = 'data prettified'


admin.site.register(EventStore, EventStoreAdmin)
