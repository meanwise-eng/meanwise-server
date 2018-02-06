from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import authentication, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import detail_route, list_route

from .models import Topic
from .serializers import TopicSerializer


class TopicsListView(APIView):

    def get(self, request):
        topics = Topic.objects.all()
        paginator = Paginator(topics, 200)
        page = request.GET.get('page', 1)

        try:
            topics = paginator.page(page)
        except PageNotAnInteger:
            topics = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of
            # results.
            topics = paginator.page(paginator.num_pages)
        serializer = TopicSerializer(topics, many=True)
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "data": serializer.data,
                    'num_pages': topics.paginator.num_pages
                }
            },
            status=status.HTTP_200_OK
        )
