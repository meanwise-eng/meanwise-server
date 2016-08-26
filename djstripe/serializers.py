# -*- coding: utf-8 -*-
"""
.. module:: dj-stripe.contrib.rest_framework.serializers
    :synopsis: dj-stripe Serializer for Subscription.

.. moduleauthor:: Philippe Luickx (@philippeluickx)

"""

from __future__ import unicode_literals

from rest_framework.serializers import ModelSerializer
from .models import CurrentSubscription, Customer, Invoice, Event
from rest_framework import serializers


class SubscriptionSerializer(ModelSerializer):

    class Meta:
        model = CurrentSubscription


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event


class CreateSubscriptionSerializer(serializers.Serializer):

    stripe_token = serializers.CharField(max_length=200)
    plan = serializers.CharField(max_length=200)


class CustomerSerializer(ModelSerializer):
    has_active_subscription = serializers.ReadOnlyField()
    can_charge = serializers.ReadOnlyField()
    invoices = InvoiceSerializer(many=True, required=False)

    class Meta:
        model = Customer


class CurrentCustomerSerializer(ModelSerializer):
    has_active_subscription = serializers.ReadOnlyField()
    can_charge = serializers.ReadOnlyField()

    class Meta:
        model = Customer


class CardSerializer(serializers.Serializer):
    number = serializers.IntegerField(
        help_text=u'The card number, as a string without any separators.',
        required=True
    )
    exp_month = serializers.IntegerField(
        help_text=u"Two digit number representing the card's expiration month.",
        required=True
    )
    exp_year = serializers.IntegerField(
        help_text=u"Two or four digit number representing the card's expiration year.",
        required=True
    )
    cvc = serializers.IntegerField(
        help_text=u'Card security code.', required=True
    )

    name = serializers.CharField(
        help_text=u"Cardholder's full name.",
        required=False,
        allow_null=True
    )
    address_line1 = serializers.CharField(required=False, allow_null=True)
    address_line2 = serializers.CharField(required=False, allow_null=True)
    address_city = serializers.CharField(required=False, allow_null=True)
    address_zip = serializers.CharField(required=False, allow_null=True)
    address_state = serializers.CharField(required=False, allow_null=True)
    address_country = serializers.CharField(required=False, allow_null=True)


class CancelSerializer(serializers.Serializer):
    confirm = serializers.BooleanField(required=True)

    def validate_confirm(self, value):
        if value is False:
            raise serializers.ValidationError(u"Please confirm to continue.")
        return value
