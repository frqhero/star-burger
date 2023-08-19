from rest_framework import serializers

from .models import Order, OrderProduct


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderDeserializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, min_length=1, write_only=True)

    class Meta:
        model = Order
        fields = [
            'address',
            'firstname',
            'lastname',
            'phonenumber',
            'products',
        ]

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        order_products = [
            OrderProduct(
                order=order, price=product['product'].price, **product
            )
            for product in products
        ]
        OrderProduct.objects.bulk_create(order_products)
        return order
