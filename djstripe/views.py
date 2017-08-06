from __future__ import unicode_literals
import decimal
import json

# from django.contrib.auth import logout as auth_logout
# from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.generic import FormView
from django.views.generic import View
from django.utils.encoding import smart_str
from django.core.exceptions import ObjectDoesNotExist

from braces.views import CsrfExemptMixin
from braces.views import FormValidMessageMixin
from braces.views import LoginRequiredMixin
# from braces.views import SelectRelatedMixin
import stripe

from .forms import PlanForm
from .mixins import PaymentsContextMixin, SubscriptionMixin
from .models import CurrentSubscription
from .models import Customer
from .models import Event
from .models import EventProcessingException
from .settings import PLAN_LIST
from .settings import PAYMENT_PLANS
from .settings import subscriber_request_callback
from .settings import CANCELLATION_AT_PERIOD_END
from .sync import sync_subscriber

from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .serializers import (SubscriptionSerializer, CreateSubscriptionSerializer,
                          CurrentCustomerSerializer, CardSerializer,
                          CustomerSerializer, EventSerializer,
                          CancelSerializer)


class StripeView(APIView):
    """ Generic API StripeView """
    permission_classes = (IsAuthenticated, )

    def get_current_subscription(self):
        try:
            return self.request.user.customer.current_subscription
        except CurrentSubscription.DoesNotExist:
            return None

    def get_customer(self):
        try:
            return self.request.user.customer
        except ObjectDoesNotExist:
            return Customer.create(
                subscriber=subscriber_request_callback(self.request)
            )


class SubscribeView(StripeView):
    """
    A REST API for Stripes implementation in the backend.
    Shows account details including customer and subscription details.
    """

    def get(self, request, *args, **kwargs):
        """
        Return the users current subscription.
        Returns with status code 200.
        """
        try:
            current_subscription = self.get_current_subscription()
            serializer = SubscriptionSerializer(current_subscription)
            print (serializer.data)
            return Response(serializer.data, status=status.HTTP_200_0K)

        except:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        """
        Create a new current subscription for the user.
        Returns with status code 201.
        """

        serializer = CreateSubscriptionSerializer(data=request.data)

        if serializer.is_valid():
            try:
                customer = self.get_customer()
                customer.update_card(serializer.data["stripe_token"])
                customer.subscribe(serializer.data["plan"])
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            except:
                # TODO
                # Better error messages
                return Response(
                    "Something went wrong processing the payment.",
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        """
        Marks the users current subscription as cancelled.
        Returns with status code 204.
        """

        try:
            customer, created = Customer.get_or_create(
                subscriber=subscriber_request_callback(self.request)
            )
            customer.cancel_subscription(
                at_period_end=CANCELLATION_AT_PERIOD_END
            )

            return Response(status=status.HTTP_204_NO_CONTENT)

        except:
            return Response(
                "Something went wrong cancelling the subscription.",
                status=status.HTTP_400_BAD_REQUEST
            )


class CurrentCustomerDetailView(StripeView, generics.RetrieveAPIView):
    """ See the current customer/user payment details """

    serializer_class = CurrentCustomerSerializer

    def get_object(self):
        return self.get_customer()

# ============================================================================ #
#                                 Billing Views                                #
# ============================================================================ #


class ChangeCardView(LoginRequiredMixin, PaymentsContextMixin, StripeView):
    """ Add or update customer card details """
    serializer_class = CardSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                validated_data = serializer.validated_data

                customer = self.get_customer()
                card_token_response = customer.create_card_token(validated_data)
                token = card_token_response[0].get('id', None)
                customer.update_card(token)
                send_invoice = customer.card_fingerprint == ""

                if send_invoice:
                    customer.send_invoice()
                    customer.retry_unpaid_invoices()

                return Response(validated_data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except stripe.CardError as e:
            error_data = {u'error': smart_str(e) or u'Unknown error'}
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)


class EventListView(StripeView, generics.ListAPIView):
    """ List customer events """
    serializer_class = EventSerializer

    def get_queryset(self):
        customer = self.get_customer()
        events = customer.event_set.all()
        return events


class HistoryView(LoginRequiredMixin, StripeView, generics.RetrieveAPIView):
    serializer_class = CustomerSerializer

    def get_object(self):
        customer = self.get_customer()
        # invoices = customer.invoices.all()

        return customer


class SyncHistoryView(CsrfExemptMixin, LoginRequiredMixin, View):
    """TODO: Needs to be refactored to leverage context data."""

    def post(self, request, *args, **kwargs):
        return self.sync_subscriber(subscriber_request_callback(request))


# ============================================================================ #
#                              Subscription Views                              #
# ============================================================================ #


class CancelSubscriptionView(StripeView):
    """ Cancel customer subscription """
    serializer_class = CancelSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            subscription = self.get_customer_subscription()
            if serializer.is_valid():
                if subscription.status == subscription.STATUS_CANCELLED:
                    return Response({'success': True}, status=status.HTTP_202_ACCEPTED)
            else:
                messages.info(self.request, "Your subscription status is now '{status}' until '{period_end}'".format(
                    status=subscription.status, period_end=subscription.current_period_end)
                )
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except stripe.StripeError as e:
            error_data = {u'error': smart_str(e) or u'Unknown error'}
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)


class ChangePlanView(LoginRequiredMixin, FormValidMessageMixin, SubscriptionMixin, APIView):
    """
    TODO: Work in a trial_days kwarg

    Also, this should be combined with ConfirmFormView.
    """
    success_url = reverse_lazy("history")
    form_class = PlanForm
    form_valid_message = "You've just changed your plan!"

    def post(self, request, *args, **kwargs):
        form = PlanForm(request.POST)
        try:
            customer = subscriber_request_callback(request).customer
        except Customer.DoesNotExist as exc:
            form.add_error(
                None,
                "You must already be subscribed to a plan before you can change it."
            )
            return self.form_invalid(form)

        if form.is_valid():
            try:
                # When a customer upgrades their plan, and DJSTRIPE_PRORATION_POLICY_FOR_UPGRADES is set to True,
                # we force the proration of the current plan and use it towards the upgraded plan,
                # no matter what DJSTRIPE_PRORATION_POLICY is set to.
                if PRORATION_POLICY_FOR_UPGRADES:
                    current_subscription_amount = customer.current_subscription.amount
                    selected_plan_name = form.cleaned_data["plan"]
                    selected_plan = [plan for plan in PLAN_LIST if plan[
                        "plan"] == selected_plan_name][0]  # TODO: refactor
                    selected_plan_price = selected_plan["price"] / decimal.Decimal("100")

                    # Is it an upgrade?
                    if selected_plan_price > current_subscription_amount:
                        customer.subscribe(selected_plan_name, prorate=True)
                    else:
                        customer.subscribe(selected_plan_name)
                else:
                    customer.subscribe(form.cleaned_data["plan"])
            except stripe.StripeError as exc:
                form.add_error(None, str(exc))
                return self.form_invalid(form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ConfirmFormView(LoginRequiredMixin, FormValidMessageMixin, SubscriptionMixin, StripeView):

    form_class = PlanForm
    form_valid_message = "You are now subscribed!"
    success_url = reverse_lazy("history")

    def get(self, request, *args, **kwargs):
        plan_slug = self.kwargs['plan']
        if plan_slug not in PAYMENT_PLANS:
            return redirect("subscribe")

        plan = PAYMENT_PLANS[plan_slug]
        customer = self.get_customer()

        if hasattr(customer, "current_subscription") and customer.current_subscription.plan == plan['plan'] and customer.current_subscription.status != CurrentSubscription.STATUS_CANCELLED:
            message = "You already subscribed to this plan"
            messages.info(request, message, fail_silently=True)
            return redirect("djstripe:subscribe")

        return super(ConfirmFormView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(ConfirmFormView, self).get_context_data(**kwargs)
        context['plan'] = PAYMENT_PLANS[self.kwargs['plan']]
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            try:
                customer = self.get_customer()
                customer.update_card(self.request.POST.get("stripe_token"))
                customer.subscribe(form.cleaned_data["plan"])
            except stripe.StripeError as exc:
                form.add_error(None, str(exc))
                return self.form_invalid(form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

# ===================================================================== #
#                              Web Services                             #
# ======================================================================#


class WebHook(CsrfExemptMixin, View):

    def post(self, request, *args, **kwargs):
        body = smart_str(request.body)
        data = json.loads(body)
        if Event.stripe_objects.exists_by_json(data):
            EventProcessingException.objects.create(
                data=data,
                message="Duplicate event record",
                traceback=""
            )
        else:
            event = Event.create_from_stripe_object(data)
            event.validate()
            event.process()
        return HttpResponse()
