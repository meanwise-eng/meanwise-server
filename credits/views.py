from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response

from credits.models import Credits
from credits.serializers import CreditsSerializer


class CreditsListView(APIView):

    def get(self, request, user_id):
        credits = Credits.objects.filter(user_id=user_id)

        serializer = CreditsSerializer(credits, many=True)

        return Response({
            'status': 'success',
            'error': None,
            'results': serializer.data
        }, status.HTTP_200_OK)
