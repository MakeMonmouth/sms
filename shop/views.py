from django.shortcuts import render, redirect

from django.conf import settings
from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt # new
from django.views.generic.base import TemplateView

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from membership.models import Membership, UserMembership, Subscription
from .models import Product, ProductCategory, Supplier


class ProductView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'shop/list.html'

    def get_user_membership(self, user):
        if user.user.username != "":
            user_membership_qs = UserMembership.objects.filter(user=user.user)
            if user_membership_qs.exists():
                return user_membership_qs.first()
        return None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_membership = self.get_user_membership(self.request)
        if current_membership is not None:
            context['current_membership'] = str(current_membership.membership)
        else:
            context['current_membership'] = None
        return context
