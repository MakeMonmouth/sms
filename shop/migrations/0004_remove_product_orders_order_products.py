# Generated by Django 4.0.1 on 2022-01-31 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_remove_order_products_product_orders'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='orders',
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(null=True, related_name='order_product', to='shop.Product'),
        ),
    ]