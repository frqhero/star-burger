from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Order, OrderProduct
from .serializers import OrderDeserializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse(
        [
            {
                'title': 'Burger',
                'src': static('burger.jpg'),
                'text': 'Tasty Burger at your door step',
            },
            {
                'title': 'Spices',
                'src': static('food.jpg'),
                'text': 'All Cuisines',
            },
            {
                'title': 'New York',
                'src': static('tasty.jpg'),
                'text': 'Food is incomplete without a tasty dessert',
            },
        ],
        safe=False,
        json_dumps_params={
            'ensure_ascii': False,
            'indent': 4,
        },
    )


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            }
            if product.category
            else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            },
        }
        dumped_products.append(dumped_product)
    return JsonResponse(
        dumped_products,
        safe=False,
        json_dumps_params={
            'ensure_ascii': False,
            'indent': 4,
        },
    )


@api_view(['POST'])
def register_order(request):
    order_deserializer = OrderDeserializer(data=request.data)
    order_deserializer.is_valid(raise_exception=True)

    data = order_deserializer.validated_data
    products = data.pop('products')
    with transaction.atomic():
        order = Order.objects.create(**data)

        order_products = [
            OrderProduct(order=order, price=product['product'].price, **product)
            for product in products
        ]
        OrderProduct.objects.bulk_create(order_products)

    serializer = OrderDeserializer(order)

    return Response(serializer.data, status=status.HTTP_201_CREATED)
