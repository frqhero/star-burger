# Generated by Django 3.2.15 on 2023-08-13 14:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_auto_20230813_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='registered_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
