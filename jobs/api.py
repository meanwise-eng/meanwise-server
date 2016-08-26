from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.middleware.csrf import get_token # will use later

from .models import Job, JobApplication
from .serializers import JobSerializer, JobAppSerializer
from account_profile.models import Profile
from company.models import Company, CompanyProfile
from company.serializers import CompanySerializer, CompanyProfileSerializer

from rest_framework.decorators import api_view # might use
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

class JobList(APIView):
    """
    List all jobs.
    """
    def get(self, request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)

    def post(self, request):
        # NOTE, there should be a permission check here.
        # Still missing csrf token check
        if request.user.is_authenticated():
            serializer = JobSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)


class CompanyJobList(APIView):
    """
    List all jobs from a given company.
    Create job endpoint
    """
    def get(self, request, company_slug):
        company = get_object_or_404(Company, slug=company_slug)
        jobs = Job.objects.filter(company=company.id)
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)

    def post(self, request, company_slug):
        company = get_object_or_404(Company, slug=company_slug)
        if request.user.is_authenticated():
            serializer = JobSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(company=company.id)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)


class JobDetail(APIView):
    """
    Retrieves, update or delete a job instance
    """
    def get(self, request, company_slug, job_slug):
        company = get_object_or_404(Company, slug=company_slug)
        job = get_object_or_404(Job, slug=job_slug, company=company.id)
        serializer = JobSerializer(job)
        # NOTE, serializer.data['company'] is the company object,
        # seen as a foreign key permission, should either allow access
        # to object (when creating) or just to name (public)
        return Response(serializer.data)

    def put(self, request, company_slug, job_slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=company_slug)
            job = get_object_or_404(Job, slug=job_slug, company=company.id)
            serializer = JobSerializer(job, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, company_slug, job_slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=company_slug)
            job = get_object_or_404(Job, slug=job_slug, company=company.id)
            job.delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)
