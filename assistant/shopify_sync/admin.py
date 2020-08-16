from django.contrib import admin

from .models import ShopifySyncLog

class ShopifySyncLogAdmin(admin.ModelAdmin):
    pass


admin.site.register(ShopifySyncLog, ShopifySyncLogAdmin)