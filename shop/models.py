from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime


from phonenumber_field.modelfields import PhoneNumberField


class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    general_email = models.EmailField()
    general_tel = PhoneNumberField()
    website_url = models.URLField()
    login_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    cost_price = models.DecimalField(default=0,
            decimal_places=2,
            max_digits=5)
    member_price = models.DecimalField(default=0,
            decimal_places=2,
            max_digits=5)
    guest_price = models.DecimalField(default=0,
            decimal_places=2,
            max_digits=5)
    rrp = models.DecimalField(default=0,
            decimal_places=2,
            max_digits=5)
    category = models.ForeignKey(ProductCategory, 
            related_name='product_category', 
            on_delete=models.SET_NULL, 
            null=True)
    supplier = models.ForeignKey(Supplier, 
            related_name='product_supplier', 
            on_delete=models.SET_NULL, 
            null=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
            related_name='product_created_by',
            on_delete=models.CASCADE)
    image = models.ImageField(upload_to=f"static/uploads/products/")

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
            related_name='user_orders',
            on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    packed = models.DateTimeField(blank=True, null=True)
    shipped = models.DateTimeField(blank=True, null=True)
    delivered = models.DateTimeField(blank=True, null=True)
    products = models.ManyToManyField(Product, 
            related_name='order_product')


    def __int__(self):
        return self.id

    def __str__(self):
        cost = 0
        total = 0
        for product in self.products.all():
            cost = cost + product.cost_price
            total = total + product.member_price

        profit = total - cost
        return f"Order {self.id} placed {naturaltime(self.created)} by {self.user.username} (cost: £{cost}, total: £{total}, profit: £{profit})"
