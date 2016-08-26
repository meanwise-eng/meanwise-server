from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

from .models import Leader, Page
from .serializers import LeaderSerializer, PageSerializer
from company.models import Company


"""
	Leader CRUD.
	Modified for nice url headings.
"""
class LeaderView(APIView):
    """
    Given a company_slug, Basic CRUD
    NOTE (PUT/DEL), request.data must have attribute 'name'
    """
    def get(self, request, company_slug):
        company = get_object_or_404(Company, slug=company_slug)
        leaders = company.leader_set.all()
        serializer = LeaderSerializer(leaders, many=True)
        return Response(serializer.data)

    def post(self, request, company_slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=company_slug)
            serializer = LeaderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(company=company)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, company_slug):
        if request.user.is_authenticated():
            leader = get_object_or_404(Leader, name=request.data['name'])
            serializer = LeaderSerializer(leader, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, company_slug):
        if request.user.is_authenticated():
            leader  = get_object_or_404(Leader, name=request.data['name'])
            leader.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)


class PageList(APIView):
    """
    CRUD pages.
    NOTE (PUT/DEL): incoming request must have attribute 'page_type'
    eg. request['page_type'] = 'company'
    """
    def get(self, request, company_slug):
        company = get_object_or_404(Company, slug=company_slug)
        page = company.page
        serializer = PageSerializer(page)
        return Response(serializer.data)

    def post(self, request, company_slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=company_slug)
            serializer = PageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(company=company)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)


class PageDetail(APIView):
    def put(self, request, company_slug, page_slug):
        if request.user.is_authenticated():
            page = get_object_or_404(Page, slug=page_slug)
            serializer = PageSerializer(page, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, company_slug, page_slug):
        if request.user.is_authenticated():
            company = get_object_or_404(Company, slug=company_slug)
            page = get_object_or_404(Page, slug=page_slug)
            page.delete()
            return Response("Deleted successfully",
                            status=status.HTTP_202_ACCEPTED)
        else:
            return Response("Not authenticated",
                            status=status.HTTP_401_UNAUTHORIZED)