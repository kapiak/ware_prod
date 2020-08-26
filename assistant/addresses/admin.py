from django.contrib import admin

from .models import Address


class AddressAdmin(admin.ModelAdmin):
    pass


admin.site.register(Address, AddressAdmin)
