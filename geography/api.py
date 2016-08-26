from django.db.models import Q

from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from common.http import JsonErrorResponse
from common.constants import UNAUTHENTICATED_NOT_LOGGEDIN

from .models import City, Location
from .utils import get_lat_lon
from .external import get_cities, get_locations
from .serializers import CitySerializer, LocationSerializer


class LocationListAPIView(ListAPIView):
    def get(self, request):
        if request.user.is_authenticated():
            q = request.GET.get('q', '')
            if q:
                lat_lon = get_lat_lon(request.ip)
                locations = get_locations(q, lat_lon)
                if not locations:
                    locations = Location.objects.filter(description__icontains=q)[0:5]
            else:
                locations = []
            serializer = LocationSerializer(locations, many=True)
            return Response({'location': serializer.data})
        else:
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)


class CityListAPIView(ListAPIView):
    def get(self, request):
        if request.user.is_authenticated():
            q = request.GET.get('q', '')
            if q:
                lat_lon = get_lat_lon(request.ip)
                cities = get_cities(q, lat_lon)
                if not cities:
                    cities = City.objects.filter(description__icontains=q)[0:5]
            else:
                cities = []
            serializer = CitySerializer(cities, many=True)
            return Response({'city': serializer.data})
        else:
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
