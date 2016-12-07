from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import User

import logging

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import authentication, permissions

from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet

from userprofile.models import Profession, Skill, Interest, UserProfile
from userprofile.serializers import *

from userprofile.search_indexes import UserProfileIndex

logger = logging.getLogger('delighter')

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


class FriendsList(APIView):
    """
    List all friends for user (user_id) and add friends

    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        """
        List all friends for user (user_id)

        """
        logger.info("Friends list - GET - FriendList [API / views.py /")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error("Friendslist - GET - User not found [api / views.py /")
            return Response({"status":"failed","error":"User with id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            up = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            logger.error("friendslist - GET - up not found [api / views.py /")
            return Response({"status":"failed","error":"Userprofile with id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        user_friends = up.friends.all()
        user_friends_profiles = []
        for user in user_friends:
            try:
                user_friends_profiles.append(UserProfile.objects.get(user=user).id)
            except UserProfile.DoesNotExist:
                pass
        serialized_friends_list = UserProfileSerializer(UserProfile.objects.filter(id__in=user_friends_profiles), many=True)

        return Response(serialized_friends_list.data, status=status.HTTP_200_OK)

    
    def post(self, request, user_id):
        """
        Add friend
        
        """
        logger.info("Friendslist - POST [API / views.py /")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error("Friendslist - GET - User not found [api / views.py /")
            return Response({"status":"failed","error":"User with id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            up = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            logger.error("friendslist - GET - up not found [api / views.py /")
            return Response({"status":"failed","error":"Userprofile with id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        friend_id = request.data.get('friend_id', None)

        try:
            friend_user = User.objects.get(id=int(friend_id))
        except User.DoesNotExist:
            logger.error("Friendslist - POST - friend User not found [api / views.py /")
            return Response({"status":"failed","error":"friend User with id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        up.friends.add(friend_user)
        
        
        logger.info("Friendslist - POST - Finished [API / views.py /")
        return Response({"status":"success", "error":"", "results":"successfully added friend"}, status=status.HTTP_201_CREATED)

class RemoveFriend(APIView):
    """
    Remove friend

    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request, user_id):
        """
        Remove friend
        
        """
        logger.info("RemoveFriend - POST [API / views.py /")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error("RemoveFriend - Post - User not found [api / views.py /")
            return Response({"status":"failed","error":"User with id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            up = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            logger.error("Removefriend - GET - up not found [api / views.py /")
            return Response({"status":"failed","error":"Userprofile with id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        friend_id = request.data.get('friend_id', None)

        try:
            friend_user = User.objects.get(id=int(friend_id))
        except User.DoesNotExist:
            logger.error("Removefriend - POST - friend User not found [api / views.py /")
            return Response({"status":"failed","error":"friend User with id does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        up.friends.remove(friend_user)
        
        
        logger.info("Friendslist - POST - Finished [API / views.py /")
        return Response({"status":"success", "error":"", "results":"successfully removed friend"}, status=status.HTTP_201_CREATED)

    
class UserProfileHSSerializer(HaystackSerializer):
    class Meta:
        index_classes = [UserProfileIndex]
        fields = [
            "first_name", "last_name"
        ]

class UserProfileSearchView(HaystackViewSet):
    index_models = [UserProfile]
    serializer_class = UserProfileHSSerializer