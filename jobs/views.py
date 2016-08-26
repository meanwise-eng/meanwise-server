from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.middleware.csrf import get_token # will use later

from .models import Job, JobApplication
from .serializers import JobSerializer, JobAppSerializer
from account_profile.models import Profile

from .serializers import JobSerializer, JobAppSerializer , CandidateViewSerializer

from company.models import Company
from company.serializers import CompanySerializer
from account_profile.models import Profile
from allauth.models import User
from haystack.generic_views import SearchView
from haystack.inputs import AutoQuery, Clean
from haystack.query import SearchQuerySet, SQ
from rest_framework import status
from rest_framework.decorators import api_view # might use
from rest_framework.response import Response
from rest_framework.views import APIView


sqs = SearchQuerySet()


class JobSearchView(SearchView):
    """
        Company Search view
    """
    def get_queryset(self):
        queryset = super(CompanySearchView, self).get_queryset()
        return queryset

    def get_queryset_by_skill(self, *args):
        sqs.models(Job).filter()


@api_view(['POST'])
def applyJob(request, company_slug, job_slug):
    """
        Requires: authenticated user and corresponding slugs.
    """
    if request.method == 'POST':
        # company = get_object_or_404(Company, slug=company_slug)
        if request.user.is_authenticated():
            profile = get_object_or_404(Profile,
                                        username=request.user.profile.username)
            job = get_object_or_404(Job, slug=job_slug)
            data = {
                'job': job.id,
                'profile': profile.id
            }
            serializer = JobAppSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response("Successfully sent job application.",
                                status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def getRecommendations(request, username):
    """
        Grabs a list of recommended jobs based on skills. Based on user skills.

        NOTE: To be the endpoint for AI app.
              This method should pull user data
                                    -> AI app
                                    -> give reccomendations
    """
    if request.method == 'GET':
        user = get_object_or_404(Profile,
                                 username=request.user.profile.username)
        skills = [skill.text.lower() for skill in user.skills]
        jobs = sqs.models(Job).filter(SQ(skills__in=skills))
        if jobs.count() == 0:
            return Response('Failed to find any jobs with this query.\
                             Try adding more information to your profile')
        instances = [job.object for job in jobResults]
        serializer = JobSerializer(instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
