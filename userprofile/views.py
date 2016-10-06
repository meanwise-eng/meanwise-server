from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.text import slugify

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import permission_classes

from userprofile.models import Profession, Skill, Interest, UserProfile
from userprofile.serializers import *


class ProfessionViewSet(viewsets.ModelViewSet):
    """
    Profession apis

    """
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'text', 'slug', 'created_on', 'last_updated', 'searchable')


class SkillViewSet(viewsets.ModelViewSet):
    """
    Skill apis

    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'text', 'lower', 'slug',
              'created_on', 'last_updated', 'searchable')


class InterestViewSet(viewsets.ModelViewSet):
    """
    Interest apis

    """
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'name', 'slug', 'description',
              'created_on', 'modified_on', 'published',
              'cover_photo', 'color_code', 'topics',
                  'is_deleted')

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.save()
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    UserProfile apis

    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'username', 'first_name', 'middle_name',
              'last_name', 'profession', 'city', 'skills',
              'interests', 'profile_photo', 'cover_photo',
              'bio', 'created_on', 'last_updated')

@permission_classes([TokenAuthentication,])
class RequestInterest(APIView):

    def post(self, request):
        logger.info("Request for interest - POST - RequestInterest [API / views.py /")
        try:
            interest_name = request.data.get('name', None)
            description = request.data.get('description', None)
            already_exists = False
            try:
                interest = Interest.objects.get(name=interest_name)
            except Interest.DoesNotExist:
                create_one = True
            except Exception as e:
                return Response({"error":sstr(e)}, status.HTTP_400_BAD_REQUEST)
            if not already_exists:
                if interest.published:
                    return Response({"message":"Interest with name already published"} ,  status.HTTP_200_OK)
                else:
                    interest.vote_count += 1
                    interest.save()
                    return Response({"message":"Succesfully submitted"} ,  status.HTTP_200_OK)
            else:
                interest = Interest.objects.create(name=interest_name, slug=slugify(name), description=description, vote_count=1)
                return Response({"message":"Succesfully submitted"} ,  status.HTTP_200_OK)
                                    
        except requests.RequestException as e:
            logger.error("Request Interest - POST - Exception: " + e.message + " [API / views.py /")
            return Response({"error":str(e)}, status.HTTP_400_BAD_REQUEST)