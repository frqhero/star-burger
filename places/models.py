from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField(max_length=200, primary_key=True, verbose_name='адрес')
    longitude = models.FloatField(verbose_name='долгота')
    latitude = models.FloatField(verbose_name='широта')
    updated_at = models.DateTimeField(verbose_name='изменен', default=timezone.now)
