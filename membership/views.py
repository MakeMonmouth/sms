import stripe

from django.shortcuts import render, redirect

from django.conf import settings
from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt # new
from django.views.generic.base import TemplateView

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from membership.models import Membership, UserMembership, StripeDetails


class MembershipView(LoginRequiredMixin, ListView):
    model = Membership
    template_name = 'memberships/list.html'


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

class ChangeMembershipView(LoginRequiredMixin, ListView):
    template_name = 'memberships/change_membership.html'
    model = Membership

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
            context['current_membership_cost'] = str(current_membership.membership.price)
            context['current_membership_sub_id'] = str(current_membership.stripe_subscription_id)
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
        domain_url = f"{request.build_absolute_uri('/')}memberships/"
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
            user = None
            user_qs = User.objects.filter(id=request.user.id)
            if user_qs.exists():
                # We have an existing user/subscription pair
                user = user_qs.first()
            
                if user.stripedetails.stripe_customer_id == "":
                    print("We have a user but not a customer ID")
                    checkout_session = stripe.checkout.Session.create(
                        client_reference_id=f"{request.user.id};{request.POST['priceId']}",
                        success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                        cancel_url=domain_url + 'cancelled/',
                        payment_method_types=['card'],
                        mode='subscription',
                        customer_email = request.user.email,
                        billing_address_collection = "required",
                        line_items=[{
                            'price': request.POST['priceId'],
                            'quantity': 1
                            }
                        ]
                    )
                else:
                    cust_id = user.stripedetails.stripe_customer_id
                    print(f"We have a customer ID: {cust_id}")
                    existing_membership = UserMembership.objects.filter(user=user).first()

                    checkout_session = stripe.checkout.Session.create(
                        client_reference_id=f"{request.user.id};{request.POST['priceId']}",
                        success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                        cancel_url=domain_url + 'cancelled/',
                        payment_method_types=['card'],
                        mode='subscription',
                        customer = request.user.stripedetails.stripe_customer_id,
                        billing_address_collection = "required",
                        line_items=[{
                            'price': request.POST['priceId'],
                            'quantity': 1
                            }
                        ]
                    )
            else:
                print("We do not have a user or customer ID")
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=f"{request.user.id};{request.POST['priceId']}",
                    success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url + 'cancelled/',
                    payment_method_types=['card'],
                    mode='subscription',
                    customer_email = request.user.email,
                    billing_address_collection = "required",
                    line_items=[{
                        'price': request.POST['priceId'],
                        'quantity': 1
                        }
                    ]
                )
            response = checkout_session.url
            return redirect(response)
        except Exception as e:
            print(f"Error: {e}")
            return redirect("/memberships/cancelled/")

    return redirect("/memberships/")

@csrf_exempt
def change_subscription(request):
    if request.method == 'POST':
        domain_url = f"{request.build_absolute_uri('/')}memberships/"
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
            user_qs = User.objects.filter(id=request.user.id)
            if user_qs.exists():
                # We have an existing user/subscription pair
                user = user_qs.first()
                existing_membership = UserMembership.objects.filter(user=user).first()

                # Get the current subscription details so we can modify them
                existing_sub = stripe.Subscription.retrieve(
                        request.POST['subId']
                        )

                esub_id = existing_sub['items']['data'][0]['id']

                newsub = stripe.Subscription.modify(
                    request.POST['subId'],
                    items=[{
                        'id': esub_id,
                        'price': request.POST['priceId'],
                        'quantity': 1
                        }
                    ]
                )
                if newsub['id'] is not None:
                    sub_level = Membership.objects.filter(stripe_price_id=request.POST['priceId']).first()
                    existing_membership.stripe_subscription_id = newsub['id']
                    existing_membership.membership = sub_level
                    existing_membership.save()
                    return redirect("/memberships/success/")
                else:
                    print("No new sub id found, change failed")
        except Exception as e:
            print(f"Error: {e}")
            return redirect("/memberships/cancelled/")

    return redirect("/memberships/")

@csrf_exempt
def cancel_subscription(request):
    if request.method == 'POST':
        domain_url = f"{request.build_absolute_uri('/')}memberships/"
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
            user_qs = User.objects.filter(id=request.user.id)
            if user_qs.exists():
                # We have an existing user/subscription pair
                user = user_qs.first()
                existing_membership = UserMembership.objects.filter(user=user).first()

                # Get the current subscription details so we can modify them
                existing_sub = stripe.Subscription.retrieve(
                        request.POST['subId']
                        )

                esub_id = existing_sub['items']['data'][0]['id']

                print("Requesting Cancellation")
                can_sub = stripe.Subscription.delete(
                        request.POST['subId']
                        )
                if can_sub['id'] is not None:
                    existing_membership.delete()
                else:
                    print("No new sub id found, change failed")
        except Exception as e:
            print(f"Error: {e}")
            return redirect("/memberships/cancelled/")

    return redirect("/memberships/")

class SuccessView(TemplateView):
    template_name = 'memberships/success.html'
    model = Membership

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
            context['current_membership_cost'] = str(current_membership.membership.price)
            context['current_membership_sub_id'] = str(current_membership.stripe_subscription_id)
        else:
            context['current_membership'] = None
        return context

class CancelledView(TemplateView):
    template_name = 'memberships/cancellation.html'
    model = Membership

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
            context['current_membership_cost'] = str(current_membership.membership.price)
            context['current_membership_sub_id'] = str(current_membership.stripe_subscription_id)
        else:
            context['current_membership'] = None
        return context


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
        sub_id = event['data']["object"]['subscription']
        cust_details = event['data']['object']['client_reference_id'].split(';')
        user_id = cust_details[0]
        price_id = cust_details[1]
        stripe_cust_id = event['data']['object']['customer']

        membership_qs = Membership.objects.filter(stripe_price_id=price_id)
        if membership_qs.exists():
            membership = membership_qs.first()

        user_qs = User.objects.filter(id=user_id)
        if user_qs.exists():
            user = user_qs.first()
            existing_membership = UserMembership.objects.filter(user=user)

        existing_stripe_details = StripeDetails.objects.filter(user=user).first()
        if not existing_stripe_details:
            nsd = StripeDetails()
            nsd.user = user
            nsd.stripe_customer_id = stripe_cust_id
            nsd.save()
        else:
            sd = existing_stripe_details
            sd.stripe_customer_id = stripe_cust_id
            sd.save()

        if not existing_membership.exists():
            newsub = UserMembership()
            newsub.user = user 
            newsub.membership = membership
            newsub.stripe_subscription_id = sub_id
            newsub.save()
        else:
            em = existing_membership.first()
            em.membership = membership
            em.stripe_subscription_id = sub_id
            em.save()

    return HttpResponse(status=200)
