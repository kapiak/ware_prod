from django.contrib import admin
from django.db.models import JSONField

from assistant.core.admin import PrettyJSONWidget

from .models import ErrorSyncLog, ShopifySyncLog


class ShopifySyncLogAdmin(admin.ModelAdmin):
    pass


admin.site.register(ShopifySyncLog, ShopifySyncLogAdmin)



class ErrorSyncLogAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }


admin.site.register(ErrorSyncLog, ErrorSyncLogAdmin)
