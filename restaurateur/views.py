import rollbar
from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.conf import settings
from geopy import distance
import requests

from foodcartapp.models import Product, Restaurant, Order
from places.models import Place


class Login(forms.Form):
    username = forms.CharField(
        label='Логин',
        max_length=75,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Укажите имя пользователя',
            }
        ),
    )
    password = forms.CharField(
        label='Пароль',
        max_length=75,
        required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}
        ),
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, 'login.html', context={'form': form})

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect('restaurateur:RestaurantView')
                return redirect('start_page')

        return render(
            request,
            'login.html',
            context={
                'form': form,
                'ivalid': True,
            },
        )


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability
            for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False)
            for restaurant in restaurants
        ]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(
        request,
        template_name='products_list.html',
        context={
            'products_with_restaurant_availability': products_with_restaurant_availability,
            'restaurants': restaurants,
        },
    )


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(
        request,
        template_name='restaurants_list.html',
        context={
            'restaurants': Restaurant.objects.all(),
        },
    )


def fetch_coordinates(address):
    try:
        place = Place.objects.get(address=address)
    except Place.DoesNotExist:
        place = Place(address=address)
        apikey = settings.YANDEX_GEOCODER_TOKEN
        base_url = 'https://geocode-maps.yandex.ru/1.x'
        response = requests.get(
            base_url,
            params={
                'geocode': address,
                'apikey': apikey,
                'format': 'json',
            },
        )
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection'][
            'featureMember'
        ]

        if not found_places:
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(' ')
        place.latitude, place.longitude = lat, lon
        place.save()
    return place.latitude, place.longitude


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.get_orders()
    for order in orders:
        restaurants = Restaurant.objects.get_capable_ones_by_order(order)
        order.restaurants = list(restaurants)
        for restaurant in order.restaurants:
            restaurant_coords = fetch_coordinates(restaurant.address)
            order_coords = fetch_coordinates(order.address)
            order_distance = round(
                distance.distance(restaurant_coords, order_coords).km, 2
            )
            restaurant.order_distance = order_distance
        sorted(
            order.restaurants, key=lambda restaurant: restaurant.order_distance
        )
    current_url = request.path
    return render(
        request,
        template_name='order_items.html',
        context={
            'order_items': orders,
            'current_url': current_url,
        },
    )
