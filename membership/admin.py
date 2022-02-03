from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Membership, UserMembership, StripeDetails
# Register your models here.
admin.site.register(Membership)
admin.site.register(UserMembership)

# Define an inline admin descriptor for StripeDetails model
# which acts a bit like a singleton
class StripeInline(admin.StackedInline):
    model = StripeDetails
    can_delete = False
    verbose_name_plural = 'stripe_details'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (StripeInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
