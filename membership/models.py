from django.utils import timezone
from django.db import models
from django.conf import settings
# Create your models here.
MEMBERSHIP_CHOICES = (
('Core', 'core'),
('Full', 'full'),
('Part Time', 'part-time')
)

class Membership(models.Model):
    slug = models.SlugField(null=True, blank=True)
    membership_type = models.CharField(
    choices=MEMBERSHIP_CHOICES, default='Full',
    max_length=30
      )
    price = models.DecimalField(default=0,
            decimal_places=2,
            max_digits=5)
    description = models.TextField(default='')
    stripe_price_id = models.CharField(default='', max_length=100)

    def __str__(self):
       return self.membership_type

class UserMembership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
            related_name='user_membership',
            on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, 
            related_name='user_membership', 
            on_delete=models.SET_NULL, 
            null=True)
    stripe_customer_id = models.CharField(default='', max_length=255)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
       #return self.user.username
       return f"{self.user.username} - {self.membership.membership_type}"

class Subscription(models.Model):
    user_membership = models.ForeignKey(UserMembership,
            related_name='subscription',
            on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
      return self.user_membership.user.username
