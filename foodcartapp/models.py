from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import F, Sum, Q, Count
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class RestaurantQuerySet(models.QuerySet):
    def get_capable_ones_by_order(self, order):
        order_products = order.products.distinct()
        restaurants = (
            Restaurant.objects.filter(
                menu_items__product__in=order_products,
                menu_items__availability=True,
            )
            .annotate(
                num_sandwiches=Count('menu_items__product', distinct=True)
            )
            .filter(num_sandwiches=len(order_products))
        )
        return restaurants


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    objects = RestaurantQuerySet.as_manager()

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = RestaurantMenuItem.objects.filter(
            availability=True
        ).values_list('product')
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    image = models.ImageField('картинка')
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже', default=True, db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [['restaurant', 'product']]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class OrderProduct(models.Model):
    order = models.ForeignKey(
        'Order', on_delete=models.CASCADE, verbose_name='заказ'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name='товар'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )


class OrderQuerySet(models.QuerySet):
    def get_orders(self):
        product_price = F('orderproduct__price')
        product_quantity = F('orderproduct__quantity')
        orders = (
            Order.objects.annotate(price=Sum(product_price * product_quantity))
            .filter(~Q(status=4))
            .order_by('status')
        )
        return orders


class Order(models.Model):
    products = models.ManyToManyField(
        Product,
        through=OrderProduct,
        verbose_name='товары',
        related_name='orders',
    )
    firstname = models.CharField(max_length=50, verbose_name='имя')
    lastname = models.CharField(max_length=50, verbose_name='фамилия')
    phonenumber = PhoneNumberField(verbose_name='телефон')
    address = models.CharField(max_length=100, verbose_name='адрес')
    objects = OrderQuerySet.as_manager()
    STATUS_CHOICES = (
        (1, 'Новый'),
        (2, 'Собрать'),
        (3, 'Доставить'),
        (4, 'Выполнен'),
    )
    status = models.PositiveIntegerField(
        verbose_name='статус', choices=STATUS_CHOICES, default=1
    )
    comment = models.TextField()
    registered_at = models.DateTimeField(
        default=timezone.now, verbose_name='время создания'
    )
    called_at = models.DateTimeField(
        null=True, blank=True, verbose_name='время звонка'
    )
    delivered_at = models.DateTimeField(
        null=True, blank=True, verbose_name='время доставки'
    )
    PAYMENT_CHOICES = (
        (1, 'Наличные'),
        (2, 'Безналичные'),
    )
    payment_method = models.PositiveIntegerField(
        verbose_name='способ оплаты', choices=PAYMENT_CHOICES, default=1
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        verbose_name='ресторан приготовления',
        null=True,
        blank=True,
    )
