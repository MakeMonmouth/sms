import stripe

from django.shortcuts import render, redirect

from django.conf import settings # new
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt # new
from django.views.generic.base import TemplateView

## views.py
from django.views.generic import ListView
from membership.models import Membership, UserMembership, Subscription
class MembershipView(ListView):
    model = Membership
    template_name = 'memberships/list.html'

    def get_user_membership(self, user):
        print(f"Looking for user {user.user}")
        user_membership_qs = UserMembership.objects.filter(user=user.user)
        if user_membership_qs.exists():
            return user_membership_qs.first()
        return None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_membership = self.get_user_membership(self.request)
        print(current_membership)
        if current_membership.membership is not None:
            context['current_membership'] = str(current_membership.membership)
        else:
            context['current_membership'] = None
        return context

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        print(request)
        domain_url = 'http://localhost:8000/memberships/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[{
                    'price': request.POST['priceId']
                    }
                ]
            )
            response = checkout_session.url
            return redirect(response)
        except Exception as e:
            print(e)
            return redirect("/memberships/cancelled/")

    return redirect("/memberships/")

class SuccessView(TemplateView):
    template_name = 'memberships/success.html'


class CancelledView(TemplateView):
    template_name = 'memberships/cancellation.html'

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here

    return HttpResponse(status=200)

#import datetime
#from django import forms
#from django.forms import ModelForm
#from django.contrib.auth.models import User
#from django.contrib.auth.forms import UserCreationForm
#from django.conf import settings
#from membership.models import Membership, UserMembership, Subscription
#class SignUpForm(UserCreationForm):
#    part_time_member = Membership.objects.get(membership_type=)
#    class Meta(UserCreationForm.Meta):
#       model = User
#    def save(self):
#      user = super().save(commit=False)
#      user.save()
#      # Creating a new UserMembership
#      user_membership = UserMembership.objects.create(user=user, membership=self.part_time_member)
#      user_membership.save()
#      # Creating a new UserSubscription
#      user_subscription = Subscription()
#      user_subscription.user_membership = user_membership
#      user_subscription.save()
#      return user
