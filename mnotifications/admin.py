import datetime

from django.contrib import admin
from django.shortcuts import redirect
from admin_views.admin import AdminViews
from django.http import HttpResponse
from django.shortcuts import render, HttpResponseRedirect

from mnotifications.models import Notification, ASNSDevice
from mnotifications.forms import *


class NotificationAdmin(admin.ModelAdmin):
    pass


class ASNSPushAdmin(AdminViews):
    admin_views = (
                    ('add_topic', 'add_topic'),
        )

    def add_topic(self, request):
        message = ""
        if request.method == 'GET':
            message = request.GET.get('message', "")
            form = AddTopicForm()
        else:
            form = AddTopicForm(request.POST) # Bind data from request.POST into a PostForm
            if form.is_valid():
                topic = form.cleaned_data['topic']
                return HttpResponseRedirect("?message=successfully added topic")
 
        return render(request, 'add_topic.html', {
            'form': form, "message":message,
        })


admin.site.register(ASNSDevice, ASNSPushAdmin)
admin.site.register(Notification, NotificationAdmin)
