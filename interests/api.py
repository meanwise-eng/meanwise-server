from django.db.models import Q

from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from common.http import JsonErrorResponse
from common.constants import UNAUTHENTICATED_NOT_LOGGEDIN


from .models import Interest
from .serializers import ProfileInterestSerializer


class InterestListAPIView(ListAPIView):

    def get_queryset(self, q, count):
        return Interest.objects.filter(Q(name__icontains=q) | Q(description__icontains=q))[:count]

    def get(self, request):
        q = request.GET.get('q', '')
        count = min(int(request.GET.get('count', 10)), 50)
        queryset = self.get_queryset(q, count)
        serializer = ProfileInterestSerializer(queryset, many=True)
        return Response({'interest': serializer.data})
