import string
import random
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail

from .models import Company, EmailConfirmation
from .serializers import CompanySerializer

from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import jwt

sqs = SearchQuerySet()

class CompanySearchView(SearchView):
    """ 
        Company Search view
    """
    def get_queryset(self):
        queryset = super(CompanySearchView, self).get_queryset()
        return queryset

size = 25
chars = string.ascii_letters + string.digits
@api_view(['POST'])
def CreateCompany(request):
    if request.method == 'POST':
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            company_obj = serializer.save()
            confirm = EmailConfirmation.objects.create(
                email=company_obj.email,
                company=company_obj,
            )
            SendEmailToken(confirm)
            return HttpResponse("An email has been sent to your email address",
                                {'data': company_obj.email})
        else:
            return Response(serializer.errors)

@api_view(['POST'])
def upload_content(request):
    if request.method == 'POST':
        pass

def ConfirmCompany(request, token):
    query = get_object_or_404(EmailConfirmation, token=token)
    if query.confirmed is True:
        return HttpResponse("Email already verified")
    else:
        query.confirmed = True
        query.save()
        return HttpResponse("Your email has been verified")


def ResendConfirmationEmail(request, email):
    query = get_object_or_404(EmailConfirmation, email=email)
    if query.confirmed is True:
        return HttpResponse("Email is already verified")
    else:
        SendEmailToken(query)
        return HttpResponse("An email has been sent to your email address")


def SendEmailToken(query):
    secret_key = ''.join(random.choice(chars) for x in range(size))
    gentoken = jwt.encode({'user': query.email},
                          secret_key, algorithm='HS256')
    query.token = gentoken
    query.save()
    message = ("Hello here is the link localhost:8000/confirm/%s" % gentoken)
    # python -m smtpd -n -c DebuggingServer localhost:1025 
    # - to check the email on local server
    send_mail("hello", message, 'hey@example.com', [query.email])
