from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import exceptions

import django.contrib.auth.password_validation as validators
from django.core.mail import EmailMultiAlternatives

import logging

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import authentication, permissions
from rest_framework.pagination import PageNumberPagination

from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet

from userprofile.models import Profession, Skill, Interest, UserProfile, UserFriend
from userprofile.serializers import *
from mnotifications.models import Notification

from userprofile.search_indexes import UserProfileIndex

logger = logging.getLogger('delighter')

class ProfessionListView(APIView):
    """
    Profession apis

    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        professions = Profession.objects.all()
        paginator = Paginator(professions, settings.REST_FRAMEWORK['PAGE_SIZE'])
        page = request.GET.get('page', 1)

        try:
            professions = paginator.page(page)
        except PageNotAnInteger:
            professions = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            professions = paginator.page(paginator.num_pages)
        serializer = ProfessionSerializer(professions, many=True)
        return Response({"status":"success", "error":"", "results":serializer.data,
                             #'has_previous_page':professions.previous_page_number(), 'has_next_page':professions.next_page_number(), 
                             'num_pages':professions.paginator.num_pages}, status=status.HTTP_200_OK)


class SkillListView(APIView):
    """
    Skill apis

    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        skills = Skill.objects.all()
        paginator = Paginator(skills, settings.REST_FRAMEWORK['PAGE_SIZE'])
        page = request.GET.get('page', 1)

        try:
            skills = paginator.page(page)
        except PageNotAnInteger:
            skills = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            skills = paginator.page(paginator.num_pages)
        serializer = SkillSerializer(skills, many=True)
        return Response({"status":"success", "error":"", "results":serializer.data,
                             #'has_previous_page':skills.previous_page_number(), 'has_next_page':skills.next_page_number(), 
                             'num_pages':skills.paginator.num_pages}, status=status.HTTP_200_OK)

class InterestListView(APIView):
    """
    Interest apis

    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        interests = Interest.objects.all()
        paginator = Paginator(interests, settings.REST_FRAMEWORK['PAGE_SIZE'])
        page = request.GET.get('page', 1)

        try:
            interests = paginator.page(page)
        except PageNotAnInteger:
            interests = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            interests = paginator.page(paginator.num_pages)
        serializer = InterestSerializer(interests, many=True)
        return Response({"status":"success", "error":"", "results":serializer.data,
                             #'has_previous_page':interests.previous_page_number(), 'has_next_page':interests.next_page_number(), 
                             'num_pages':interests.paginator.num_pages}, status=status.HTTP_200_OK)
   

class UserProfileList(APIView):
    """
    List all Users .
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        userprofiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(userprofiles, many=True)
        return Response({"status":"success", "error":"", "results":serializer.data}, status=status.HTTP_200_OK)

class UserProfileDetail(APIView):
    """
    Edit a userprofile instance.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            userprofile = UserProfile.objects.get(user=user)
        except User.DoesNotExist:
            return Response({"status":"failed", "error":"User not found", "results":""}, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({"status":"failed", "error":"UserProfile not found", "results":""}, status=status.HTTP_400_BAD_REQUEST)
        return userprofile

    def get(self, request, user_id):
         userprofile = self.get_object(user_id)
         serializer = UserProfileSerializer(userprofile)
         return Response({"status":"success", "error":"", "results":serializer.data}, status=status.HTTP_200_OK)
     
    def patch(self, request, user_id):
        data = request.data
        userprofile = self.get_object(user_id)
        serialized_up = UserProfileSerializer(userprofile, data=data, partial=True)
        if serialized_up.is_valid():
            serialized_up.save()
            return Response({"status":"success", "error":"", "results":serialized_up.data}, status=status.HTTP_201_CREATED)
        return Response({"status":"failed", "error":serialized_up.errors, "results":""}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"status":"failed","error":"User with id does not exist", "results":""}, status=status.HTTP_400_BAD_REQUEST)
        try:
            up = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            logger.error("friendslist - GET - up not found [api / views.py /")
            return Response({"status":"failed","error":"Userprofile with id does not exist", "results":""}, status=status.HTTP_400_BAD_REQUEST)
        f_status = request.query_params.get('status', 'AC')
        if f_status.lower() == 'pending':
            user_friends = UserFriend.objects.filter(user=user).filter(status='PE')
            user_friends_reverse = UserFriend.objects.filter(friend=user).filter(status='PE')
        else:
            user_friends = UserFriend.objects.filter(user=user).filter(status='AC')
            user_friends_reverse = UserFriend.objects.filter(friend=user).filter(status='AC')
        user_friends_profiles = []
        for userfriend in user_friends:
            try:
                user_friends_profiles.append(UserProfile.objects.get(user=userfriend.friend).id)
            except UserProfile.DoesNotExist:
                pass
        for userfriendr in user_friends_reverse:
            try:
                user_friends_profiles.append(UserProfile.objects.get(user=userfriendr.user).id)
            except UserProfile.DoesNotExist:
                pass
            
        serialized_friends_list = UserProfileSerializer(UserProfile.objects.filter(id__in=user_friends_profiles), many=True)

        return Response({"status":"success", "error":"", "results":serialized_friends_list.data}, status=status.HTTP_200_OK)

    
    def post(self, request, user_id):
        """
        Friend request, accept, reject
        
        """
        logger.info("Friendslist - POST [API / views.py /")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error("Friendslist - GET - User not found [api / views.py /")
            return Response({"status":"failed","error":"User with id does not exist","results":""}, status=status.HTTP_400_BAD_REQUEST)
        try:
            up = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            logger.error("friendslist - GET - up not found [api / views.py /")
            return Response({"status":"failed","error":"Userprofile with id does not exist","results":""}, status=status.HTTP_400_BAD_REQUEST)
        friend_id = request.data.get('friend_id', None)
        friend_status = request.data.get('status', 'pending')

        #check if request for self, if so raise error
        if friend_id:
            if int(friend_id) == int(user_id):
                return Response({"status":"failed","error":"Can't send friend request for self","results":""}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            friend_user = User.objects.get(id=int(friend_id))
        except User.DoesNotExist:
            friend_user = None
            pass

        if not friend_user:
            logger.error("Friendslist - POST - friend User not found [api / views.py /")
            return Response({"status":"failed","error":"friend User with id does not exist","results":""}, status=status.HTTP_400_BAD_REQUEST)
        #check if record already exists, if already rejected, ignore
        try:
            uf = UserFriend.objects.get(user=user, friend=friend_user)
        except UserFriend.DoesNotExist:
            try:
                uf = UserFriend.objects.get(user=friend_user, friend = user)
            except UserFriend.DoesNotExist:
                uf = None
                pass
        if friend_status.lower() == "pending":
            if not uf:
                uf = UserFriend.objects.create(user=user, friend=friend_user)
                #Add notification
                notification = Notification.objects.create(receiver=user, notification_type='FR',  user_friend=uf)
                logger.info("Friendslist - POST - Finished [API / views.py /")
                return Response({"status":"success", "error":"", "results":"successfully added friend request"}, status=status.HTTP_201_CREATED)
            else:
                if uf.status.lower() == 're':
                    logger.info("Friendslist - POST - Finished [API / views.py /")
                    return Response({"status":"failed", "error":"Already rejected.", "results":""}, status=status.HTTP_201_CREATED)
                elif uf.status.lower() == 'ac':
                    logger.info("Friendslist - POST - Finished [API / views.py /")
                    return Response({"status":"success", "error":"", "results":"Already accepted"}, status=status.HTTP_201_CREATED)
                elif uf.status.lower() == 'pe':
                    logger.info("Friendslist - POST - Finished [API / views.py /")
                    return Response({"status":"success", "error":"", "results":"Request already pending"}, status=status.HTTP_201_CREATED)
                
        elif friend_status.lower() == 'accepted':
            if not uf:
                logger.error("Friendslist - POST - Userfriend not found [api / views.py /")
                return Response({"status":"failed","error":"UserFriend record with ids does not exist","results":""}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if uf.status.lower() == 're':
                    logger.info("Friendslist - POST - Finished [API / views.py /")
                    return Response({"status":"failed", "error":"Already rejected.", "results":""}, status=status.HTTP_201_CREATED)
                elif uf.status.lower() == 'ac':
                    logger.info("Friendslist - POST - Finished [API / views.py /")
                    return Response({"status":"success", "error":"", "results":"Already accepted"}, status=status.HTTP_201_CREATED)
                elif uf.status.lower() == 'pe':
                    uf.status = 'AC'
                    uf.save()
                    #Add notification
                    notification = Notification.objects.create(receiver=user, notification_type='FA',  user_friend=uf)
                    logger.info("Friendslist - POST - Finished [API / views.py /")
                    return Response({"status":"success", "error":"", "results":"Successfully accepted."}, status=status.HTTP_201_CREATED)
        elif friend_status.lower() == 'rejected':
            if not uf:
                logger.error("Friendslist - POST - Userfriend not found [api / views.py /")
                return Response({"status":"failed","error":"UserFriend record with ids does not exist","results":""}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if uf.status.lower() == 're':
                    logger.info("Friendslist - POST - Finished [API / views.py /")
                    return Response({"status":"failed", "error":"Already rejected.", "results":""}, status=status.HTTP_201_CREATED)
                elif uf.status.lower() == 'ac':
                    logger.info("Friendslist - POST - Finished [API / views.py /")
                    return Response({"status":"success", "error":"", "results":"Already accepted"}, status=status.HTTP_201_CREATED)
                elif uf.status.lower() == 'pe':
                    uf.status = 'RE'
                    uf.save()
                    logger.info("Friendslist - POST - Finished [API / views.py /")
                    return Response({"status":"success", "error":"", "results":"Successfully rejected."}, status=status.HTTP_201_CREATED)
                
        
        logger.info("Friendslist - POST - Finished [API / views.py /")
        return Response({"status":"failed","error":"Unknown","results":"Could not update status."}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"status":"failed","error":"User with id does not exist","results":""}, status=status.HTTP_400_BAD_REQUEST)
        try:
            up = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            logger.error("Removefriend - GET - up not found [api / views.py /")
            return Response({"status":"failed","error":"Userprofile with id does not exist","results":""}, status=status.HTTP_400_BAD_REQUEST)
        friend_id = request.data.get('friend_id', None)

        try:
            friend_user = User.objects.get(id=int(friend_id))
        except User.DoesNotExist:
            logger.error("Removefriend - POST - friend User not found [api / views.py /")
            return Response({"status":"failed","error":"friend User with id does not exist","results":""}, status=status.HTTP_400_BAD_REQUEST)

        up.friends.remove(friend_user)
        
        
        logger.info("Friendslist - POST - Finished [API / views.py /")
        return Response({"status":"success", "error":"", "results":"successfully removed friend"}, status=status.HTTP_201_CREATED)

class ChangePasswordView(APIView):
    """
    An endpoint for changing password.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = ChangePasswordSerializer
    model = UserProfile
    permission_classes = (IsAuthenticated,)

    def get_object(self, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"status":"failed", "error":"User not found", "results":""}, status=status.HTTP_400_BAD_REQUEST)
        return user

    def post(self, request, user_id):
        self.object = self.get_object(user_id)
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"status":"failed", "error":"Wrong old password", "results":""}, status=status.HTTP_400_BAD_REQUEST)
            #check new password
            errors = dict()
            try:
                validators.validate_password(password=serializer.data.get("new_password"), user=User)
            except exceptions.ValidationError as e:
                errors['password'] = list(e.messages)
            if errors:
                return Response({"status":"failed", "error":errors, "results":""}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"status":"success", "error":"", "results":"successfully changes password"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    """
    An endpoint for forgotten password.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = ChangePasswordSerializer
    model = UserProfile
    permission_classes = (IsAuthenticated,)

    def get_object(self, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"status":"failed", "error":"User not found", "results":""}, status=status.HTTP_400_BAD_REQUEST)
        return user

    def get(self, request, user_id):
        self.object = self.get_object(user_id)
        if not self.object.email:
            return Response({"status":"failed", "error":"User has not valid email to send new password", "results":""}, status=status.HTTP_400_BAD_REQUEST)
        # set_password also hashes the password that the user will get
        password = User.objects.make_random_password()
        self.object.set_password(password)
        self.object.save()
        try:
            subject, from_email, to = 'New password', 'hello@meanwise.com', self.object.email
            text_content = 'New generated password - ' + str(password) + ' .'
            html_content = '<p>New generated password - ' + str(password) + '.</p>'
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            return Response({"status":"failed", "error":"Could not email the new password", "results":""}, status=status.HTTP_400_BAD_REQUEST)

        
        return Response({"status":"success", "error":"", "results":"successfully sent email with new password"}, status=status.HTTP_200_OK)
    
class UserProfileHSSerializer(HaystackSerializer):
    class Meta:
        index_classes = [UserProfileIndex]
        fields = [
            "text", "id", "first_name", "last_name", "username", "skills_text"
        ]

class UserProfileSearchView(HaystackViewSet):
    index_models = [UserProfile]
    serializer_class = UserProfileSearchSerializer
    
    def filter_queryset(self, *args, **kwargs):
        queryset = super(UserProfileSearchView, self).filter_queryset(self.get_queryset())
        return queryset.order_by('-created_on')