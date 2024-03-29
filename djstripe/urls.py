# -*- coding: utf-8 -*-
"""
Wire this into the root URLConf this way::

    url(r'^stripe/', include('djstripe.urls', namespace="djstripe")),
    # url can be changed
    # Call to 'djstripe.urls' and 'namespace' must stay as is

Call it from reverse()::

    reverse("djstripe:subscribe")

Call from url tag::

    {% url 'djstripe:subscribe' %}

"""

from __future__ import unicode_literals
from django.conf.urls import url

from . import settings as app_settings
from . import views


urlpatterns = [

    url(
        r'^current-user/$',
        views.CurrentCustomerDetailView.as_view(),
        name='stripe-current-customer-detail'
    ),
    url(
        r"^subscribe/$",
        views.SubscribeView.as_view(),
        name="subscribe"
    ),
    url(
        r"^confirm/(?P<plan>.+)$",
        views.ConfirmFormView.as_view(),
        name="confirm"
    ),
    url(
        r"^change/plan/$",
        views.ChangePlanView.as_view(),
        name="change_plan"
    ),
    url(
        r"^change/cards/$",
        views.ChangeCardView.as_view(),
        name="change_card"
    ),
    url(
        r"^cancel/subscription/$",
        views.CancelSubscriptionView.as_view(),
        name="cancel_subscription"
    ),
    url(
        r"^event/$",
        views.EventListView.as_view(),
        name="event"
    ),
    url(
        r"^history/$",
        views.HistoryView.as_view(),
        name="history"
    ),
    # url(
    #     r'^cancel/$',
    #     views.CancelSubscriptionView.as_view(),
    #     name='stripe-cancel'
    # ),

    # Web services
    url(
        r"^sync/history/$",
        views.SyncHistoryView.as_view(),
        name="sync_history"
    ),

    # Webhook
    url(
        app_settings.DJSTRIPE_WEBHOOK_URL,
        views.WebHook.as_view(),
        name="webhook"
    ),
]
