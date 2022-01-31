### urls.py
from django.urls import path, include 

from . import views

app_name = 'shop'

urlpatterns = [
       path('', views.ProductView.as_view(), name='select'),
]
