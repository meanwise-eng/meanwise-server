from django.db.models import ObjectDoesNotExist

from haystack.query import SearchQuerySet
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

# from common.resources import DefaultResource
from common.http import JsonErrorResponse
from common.constants import UNAUTHENTICATED_NOT_LOGGEDIN, UNAUTHORIZED, GENERIC_ERROR_RESPONSE

from .models import Profile, Skill, LookingFor, Profession, Language
from .constants import PROFILE_NOT_FOUND
from .serializers import PublicProfileDetailSerializer, DefaultProfileDetailSerializer,\
        OwnProfileDetailSerializer, UpdateProfileDetailSerializer, SkillSerializer, LanguageSerializer,\
        LookingForSerializer, ProfessionSerializer


class ProfileAPIViewSet(viewsets.ModelViewSet):
    '''
    This is a View class for handling Profile Details.
    Profile is created at the time of registration. So no POST.
    This should only support GET & POST
    '''
    model               = Profile
    lookup_value_regex  = '[0-9a-z_.]+'
    serializer_class    = DefaultProfileDetailSerializer

    def _get_profile(self, pk):
        return Profile.objects.get_by_username_id(pk)

    def list(self, request):
        # get list of profiles
        if not request.user.is_authenticated():
            # Unauthenticated user can not make calls other than GET Profile
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        ids = request.query_params.getlist('ids[]') # Fetch at max 10 profiles at once
        ids = [int(x) for x in ids][:10]
        profiles = Profile.objects.filter(id__in=ids)
        serializer = self.get_serializer_class()(profiles, many=True)
        return Response({'profile': serializer.data})

    def create(self, request):
        # Not happening
        pass

    def partial_update(self, request, pk):
        user = request.user
        if not user.is_authenticated():
            # Unauthenticated user can not make calls other than GET Profile
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        else:
            try:
                profile = self._get_profile(pk)
            except ObjectDoesNotExist as e:
                return JsonErrorResponse(PROFILE_NOT_FOUND, status=404)
            if profile != user.profile:
                # Only the guy himself can edit his/her profile
                return JsonErrorResponse(UNAUTHORIZED, status=403)
            else:
                serializer = UpdateProfileDetailSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.update(profile)
                    return Response({'profile': serializer.validated_data})
                else:
                    return JsonErrorResponse(GENERIC_ERROR_RESPONSE)

    def retrieve(self, request, pk):
        user = request.user
        count_hit = True
        if not user.is_authenticated() and pk == 'me':
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN)
        else:
            try:
                if user.is_authenticated() and ((pk.isdigit() \
                        and user.profile.id == int(pk)) \
                        or user.profile.username == pk or pk == 'me'):
                    # User is requesting self profile
                    profile = request.user.profile
                    count_hit = False
                else:
                    # Authenticated user is requesting another user's profile
                    profile = self._get_profile(pk)
            except ObjectDoesNotExist as e:
                return JsonErrorResponse(PROFILE_NOT_FOUND, status=404)

        if count_hit:
            hit_count = HitCount.objects.get_for_object(profile)
            hit_count_response = HitCountMixin.hit_count(request, hit_count)

        serialized = Profile.cache.serialized(profile, DefaultProfileDetailSerializer)
        return Response({'profile': serialized})

class SkillListAPIView(ListAPIView):
    #TODO Abstract searchable APIs that rely on indexes into a new sub class

    def get_queryset(self, q, count):
        if q:
            qs = SearchQuerySet().autocomplete(content_auto=q).models(Skill)[:count]
        else:
            qs = Skill.objects.order_by('?')[:count]
        return qs

    def get(self, request):
        #TODO abstract this in a auth class
        if request.user.is_authenticated():
            q = request.GET.get('q', '')
            count = min(int(request.GET.get('count', 5)), 20)
            queryset = self.get_queryset(q, count)
            skill_ids = []
            for result in queryset:
                if result: skill_ids.append(result.pk)
            skills = Skill.objects.filter(pk__in=skill_ids)
            serializer = SkillSerializer(skills, many=True)
            return Response({'skill': serializer.data})
        else:
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)

class LookingForListAPIView(ListAPIView):

    def get_queryset(self):
        return LookingFor.objects.filter(published=True)

    def get(self, request):
        #TODO abstract this in a auth class
        if request.user.is_authenticated():
            queryset = self.get_queryset()
            serializer = LookingForSerializer(queryset, many=True)
            return Response({'lookingFor': serializer.data})
        else:
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)

class ProfessionListAPIView(ListAPIView):

    def get_queryset(self, q, count):
        if q:
            qs = SearchQuerySet().autocomplete(content_auto=q).models(Profession)[:count]
        else:
            qs = SearchQuerySet().all().models(Profession)[:count]
        return qs

    def get(self, request):
        #TODO abstract this in a auth class
        if request.user.is_authenticated():
            q = request.GET.get('q', '')
            count = min(int(request.GET.get('count', 5)), 10)
            queryset = self.get_queryset(q, count)
            profession_ids = []
            for result in queryset:
                if result: profession_ids.append(result.pk)
            professions = Profession.objects.filter(pk__in=profession_ids)
            serializer = ProfessionSerializer(professions, many=True)
            return Response({'profession': serializer.data})
        else:
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)

class LanguageListAPIView(ListAPIView):

    def get_queryset(self, q, count):
        if q:
            qs = SearchQuerySet().autocomplete(content_auto=q).models(Language)[:count]
        else:
            qs = SearchQuerySet().all().models(Language)[:count]
        return qs

    def get(self, request):
        #TODO abstract this in a auth class
        if request.user.is_authenticated():
            q = request.GET.get('q', '')
            count = min(int(request.GET.get('count', 5)), 10)
            queryset = self.get_queryset(q, count)
            language_ids = []
            for result in queryset:
                if result: language_ids.append(result.pk)
            languages = Language.objects.filter(pk__in=language_ids)
            serializer = LanguageSerializer(languages, many=True)
            return Response({'language': serializer.data})
        else:
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
