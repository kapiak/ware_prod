from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Product, ProductVariant


class VariantInline(admin.TabularInline):
    model = ProductVariant


class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_type", "title", "slug", "updated_at")
    search_fields = (
        "guid",
        "title",
    )
    inlines = (VariantInline,)


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "meta",
        "sku",
        "barcode",
        "name",
        "updated_at",
    )
    search_fields = ("product__title", "metadata")

    def meta(self, obj):
        value = obj.metadata
        if value:
            return value
        return ''

    meta.short_description = _("Shopify Id")


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
