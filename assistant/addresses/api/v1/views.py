from rest_framework.generics import ListCreateAPIView
from rest_framework import serializers

from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField

from assistant.addresses.models import Address


class AddressListCreateAPIView(ListCreateAPIView):
    """
    View to list all addresses in the system or create a new address.
    """
    
    class AddressSerializer(serializers.Serializer):
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        company_name = serializers.CharField()
        street_address_1 = serializers.CharField()
        street_address_2 = serializers.CharField()
        city = serializers.CharField()
        city_area = serializers.CharField(max_length=128)
        postal_code = serializers.CharField(max_length=20)
        country = CountryField()
        country_area = serializers.CharField(max_length=128)
        phone = PhoneNumberField()

        def create(self, validated_data):
            obj = Address.objects.create(created_by=self.context['request'].user, **validated_data)
            return obj

    filter_backends = []
    queryset = Address.objects.all()
    serializer_class = AddressSerializer