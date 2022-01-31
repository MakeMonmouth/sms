from django.contrib import admin

from .models import Product, Supplier, ProductCategory, Order
# Register your models here.
admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(ProductCategory)
admin.site.register(Order)
