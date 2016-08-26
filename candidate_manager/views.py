from django.shortcuts import render

from django.shortcuts import get_object_or_404

from .serializers import  CandidateViewSerializer

from account_profile.models import Profile

from allauth.models import User
from jobs.models import Job , JobApplication
from rest_framework.decorators import api_view # might use

from rest_framework.response import Response

@api_view(['POST'])
def view_candidate(request, company_slug, job_slug):
    print (company_slug, job_slug)
    if request.method == 'POST':
        job = get_object_or_404(Job , slug=job_slug)
        
        application = get_object_or_404(JobApplication , job = job)
        profile =  Profile.objects.get(user = User.objects.get(email=application.email))

        serializer  = CandidateViewSerializer(profile)

        return Response(serializer.data)


