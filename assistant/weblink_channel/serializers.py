from django.conf import settings

from rest_framework import serializers
from django_countries.serializer_fields import CountryField


class ProductURLSerializer(serializers.Serializer):
    link = serializers.URLField()


class CustomerSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    city = serializers.CharField()
    state = serializers.CharField()
    country = CountryField()
    code = serializers.CharField()


class ShippingSerializer(serializers.Serializer):
    method = serializers.CharField()
    weight = serializers.IntegerField()


class ProductCartSerializer(serializers.Serializer):
    url = serializers.URLField()
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    )
    comments = serializers.CharField()


class CartSerializer(serializers.Serializer):
    customer = CustomerSerializer()
    shipping = ShippingSerializer()
    items = ProductCartSerializer(many=True)
