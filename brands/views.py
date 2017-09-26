from rest_framework import status
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from rest_framework import authentication, permissions

from .models import Brand
from .serializers import BrandSerializer


class BrandDetailsView(APIView):

    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.AllowAny, )

    def get(self, request, brand_id):
        try:
            brand = Brand.objects.get(pk=brand_id)
        except Brand.DoesNotExist:
            raise Http404

        serializer = BrandSerializer(brand)

        return Response({
            'status': 'success',
            'error': None,
            'results': serializer.data
        }, status.HTTP_200_OK)
