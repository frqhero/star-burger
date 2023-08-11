from rest_framework import serializers

from .models import Order, OrderProduct


class OrderProduct(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderDeserializer(serializers.ModelSerializer):
    products = OrderProduct(many=True, min_length=1, write_only=True)

    class Meta:
        model = Order
        fields = '__all__'
