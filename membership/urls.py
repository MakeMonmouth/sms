### urls.py
from django.urls import path, include 

from . import views

app_name = 'membership'

urlpatterns = [
       path('', views.MembershipView.as_view(), name='select'),
       path('config/', views.stripe_config),
       path('create-checkout-session/', views.create_checkout_session), # new
       path('success/', views.SuccessView.as_view()), # new
       path('cancelled/', views.CancelledView.as_view()), # new
       path('webhook/', views.stripe_webhook), # new
       path('change-subscription/', views.ChangeMembershipView.as_view(), name='update'), # new
       path('change-subscription-checkout/', views.change_subscription), # new
]
