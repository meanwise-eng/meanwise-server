from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Company, CompanyProfile, CompanyLocation, CompanyCulture
from .serializers import (CompanySerializer, CompanyProfileSerializer,
                          CompanyLocationSerializer, CompanyCultureSerializer)


class CompanyList(APIView):
    """
    List all companies, or create a new company.
    """
    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)

    def post(self, request):
        if "verified" in request.data:
            del request.data['verified']

        serializer = CompanySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyDetail(APIView):
    """
    Retrieve, update or delete a company.
    """
    def get(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        serializer = CompanySerializer(company)
        return Response(serializer.data)

    def put(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        company.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)


class CompanyProfileCRUD(APIView):
    """
        CRUD Endpoint for CompanyProfile.
        {
            company_description
            company_size
            company_email
            industry
            date_founded
            company_type
            company_vision
            growth_plans
        }
    """
    def get(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        serializer = CompanyProfileSerializer(company.profile)
        return Response(serializer.data)

    def post(self, request, slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=slug)
            serializer = CompanyProfileSerializer(data=request.data)
            if serializer.is_valid():
                profile = serializer.save(name=company.company_name)
                company.profile = profile
                company.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=slug)
            if company.profile:
                serializer = CompanyProfileSerializer(company.profile, data=request.data, 
                                                      partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('No existing company profile.',
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=slug)
            company.profile.delete()
            return Response("Deleted.")
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)


class CompanyLocationCRUD(APIView):
    """
        CRUD Endpoint for CompanyLocation.
        Required fields.
        {
            name
            isHQ
            lon
            lat
        }
    """
    def get(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        locations = company.profile.offices.all()
        serializer = CompanyLocationSerializer(locations, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=slug)
            profile = company.profile
            serializer = CompanyLocationSerializer(data=request.data)
            if serializer.is_valid():
                location = serializer.save()
                profile.offices.add(location)
                profile.save
                return Response("Successfully added location",
                                status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=slug)

            if company.profile:
                serializer = CompanyProfileSerializer(company.profile, data=request.data, 
                                                      partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('No existing company profile.',
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=slug)
            company.profile.delete()
            return Response("Deleted.")
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)

class CompanyCultureCRUD(APIView):
    """
        CRUD Endpoint for CompanyCulture.

        Necessary fields for POST
        {
            'influence'
            'adventurous'
            'achievement'
            'col_ind'
            'openness'
            'pub_vs_priv'
        }
    """
    def get(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        proifle = company.profile
        if hasattr(profile, 'culture'):
            serializer = CompanyCultureSerializer(profile.culture)
            return Response(serializer.data)
        else:
            return Response("Company has no record of cultural values.",
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=slug)
            profile = company.profile
            serializer = CompanyCultureSerializer(data=request.data)
            culture = serializer.save()
            profile.culture = culture
            profile.save()
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=slug)
            profile = company.profile
            if profile:
                serializer = CompanyCultureSerializer(profile.culture, data=request.data, 
                                                      partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data,
                                    status=status.HTTP_202_ACCEPTED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('No existing company profile.',
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=slug)
            company.profile.delete()
            return Response("Deleted.")
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)





