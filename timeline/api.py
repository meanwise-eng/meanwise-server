from django.db.models import ObjectDoesNotExist

from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from haystack.query import SearchQuerySet

from account_profile.models import Profile
from common.http import JsonErrorResponse
from common.constants import (UNAUTHENTICATED_NOT_LOGGEDIN,
                              GENERIC_ERROR_RESPONSE,
                              UNAUTHORIZED, PERMISSION_ERROR_RESPONSE)

from .models import Event, CourseMajor
from .constants import EventType
from .serializers import (EventSerializer, AcademicEventUpdateSerializer,
                          ProfessionalEventUpdateSerializer,
                          OtherEventUpdateSerializer,
                          CourseMajorSerializer,
                          AchievementEventUpdateSerializer,
                          EventEventUpdateSerializer,
                          ProjectEventUpdateSerializer)


class EventAPIViewSet(viewsets.ModelViewSet):
    '''
    This class provides list, create, update, partial_update, and retrieve
    methods. update is disabled as we do not support PUT requests.
    Above methods are main function responsible for returning responses.

    ModelViewSet also profile hooks like perform_Create, perform_update which are
    passed serializer instance and can be used to modify any data before saving,
    or creating objects. In case defaul methods are sufficient do not override them.
    Else override them and write your custom code.

    For reference see `rest_framework/mixins.py` and checkout `CreateModelMixin`
    '''
    model = Event
    serializer_class = EventSerializer

    def get_queryset(self, username):
        profile = Profile.objects.get_by_username_id(username)
        return Event.objects.live().filter(profile=profile)

    def get_serializer_class(self, event_type=None):
        if event_type == EventType.ACADEMIC:
            serializer_class = AcademicEventUpdateSerializer
        elif event_type == EventType.PROFESSIONAL:
            serializer_class = ProfessionalEventUpdateSerializer
        elif event_type == EventType.OTHER:
            serializer_class = OtherEventUpdateSerializer
        elif event_type == EventType.ACHIEVEMENT:
            serializer_class = AchievementEventUpdateSerializer
        elif event_type == EventType.EVENT:
            serializer_class = EventEventUpdateSerializer
        elif event_type == EventType.PROJECT:
            serializer_class = ProjectEventUpdateSerializer
        else:
            raise Exception('Invalid event type')
        return serializer_class

    def retrieve(self, request, pk):
        raise Exception('Not Implemented')

    def list(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        if not username:
            return JsonErrorResponse(GENERIC_ERROR_RESPONSE)
        try:
            profile = Profile.objects.get_by_username_id(username)
        except ObjectDoesNotExist as e:
            return Response({'event': []})
        events = Event.cache.serialized(profile, EventSerializer)
        return Response({'event': events})

    def create(self, request):
        '''
        Create a new event. This
        '''
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        data = request.data.get('event', {})
        profile = request.user.profile
        event_type = data.get('type')
        context = {
            'profile': request.user.profile,
            'type': event_type
        }
        serializer_class = self.get_serializer_class(event_type)
        serializer = serializer_class(data=data, context=context)

        if serializer.is_valid():
            event = serializer.create_or_update(serializer.validated_data)
            event_data = EventSerializer(event).data
            return Response({'event': event_data})
        else:
            print (serializer.errors)
            return JsonErrorResponse(GENERIC_ERROR_RESPONSE)

    def update(self, request, pk):
        '''
        Update an existing event
        '''
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)

        try:
            event = Event.objects.get(pk=pk)

        except ObjectDoesNotExist as e:
            return JsonErrorResponse(EVENT_NOT_FOUND_ERROR)

        profile = request.user.profile
        if not (event.profile == profile):
            return JsonErrorResponse(PERMISSION_ERROR_RESPONSE, status=403)

        data = request.data.get('event', {})
        context = {
            'profile': request.user.profile,
            'type': event.type
        }
        serializer = self.get_serializer_class(event.type)(data=data,
                                                           context=context,
                                                           partial=True)
        if serializer.is_valid():
            event = serializer.create_or_update(serializer.validated_data,
                                                event)
            event_data = EventSerializer(event).data
            return Response({'event': event_data})
        else:
            print (serializer.errors)
            return JsonErrorResponse(GENERIC_ERROR_RESPONSE)

    def partial_update(self, request, pk):
        '''
        For PATCH. Use PUT.
        '''
        raise Exception('Not Implemented')

    def destroy(self, request, pk, **kwargs):
        '''
        For DELETE. Deleting an event.
        '''
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        try:
            event = Event.objects.get(pk=pk)
        except ObjectDoesNotExist as e:
            return Response(status=404)
        if event.profile == request.user.profile:
            event.delete()
            return Response(status=204)
        else:
            return Response(UNAUTHORIZED, status=403)


class CourseMajorAPIView(ListAPIView):

    def get_queryset(self, q, count):
        if q:
            qs = SearchQuerySet().autocomplete(content_auto=q).models(CourseMajor)[:count]
        else:
            qs = SearchQuerySet().all().models(CourseMajor)[:count]
        return qs

    def get(self, request):
        # TODO abstract this in a auth class
        if request.user.is_authenticated():
            q = request.GET.get('q', '')
            count = min(int(request.GET.get('count', 5)), 10)
            queryset = self.get_queryset(q, count)
            major_ids = []
            for result in queryset:
                if result:
                    major_ids.append(result.pk)
            majors = CourseMajor.objects.filter(pk__in=major_ids)
            serializer = CourseMajorSerializer(majors, many=True)
            return Response({'major': serializer.data})
        else:
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
