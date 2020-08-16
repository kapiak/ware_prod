from django.contrib import admin

from .models import Product, ProductVariant


class ProductAdmin(admin.ModelAdmin):
    pass


class ProductVariantAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
