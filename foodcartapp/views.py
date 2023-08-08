import json

from django.http import JsonResponse
from django.templatetags.static import static
from django.shortcuts import get_object_or_404


from .models import Product, Order, OrderProduct


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


def register_order(request):
    data = json.loads(request.body.decode())
    order = Order(
        address=data['address'],
        firstname=data['firstname'],
        lastname=data['lastname'],
        phonenumber=data['phonenumber'],
    )
    order.clean()
    order.save()
    for product in data['products']:
        product_obj = get_object_or_404(Product, id=product['product'])
        OrderProduct.objects.create(
            order=order, product=product_obj, quantity=product['quantity']
        )
    return JsonResponse({})
