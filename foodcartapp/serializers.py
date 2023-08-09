from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField


class OrderDeserializer(serializers.Serializer):
    products = serializers.ListField(allow_empty=False)
    firstname = serializers.CharField(allow_blank=False)
    lastname = serializers.CharField(allow_blank=False)
    phonenumber = PhoneNumberField(allow_blank=False)
    address = serializers.CharField(allow_blank=False)
