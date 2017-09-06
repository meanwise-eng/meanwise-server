import math

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import exceptions
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404

import django.contrib.auth.password_validation as validators
from django.core.mail import EmailMultiAlternatives

import logging
import json

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import authentication, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import detail_route, list_route

from elasticsearch_dsl import query

from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet
from drf_haystack.filters import HaystackAutocompleteFilter

from userprofile.models import Profession, Skill, Interest, UserProfile, UserFriend, FriendRequest
from userprofile.serializers import *
from .documents import Influencer
from mnotifications.models import Notification

from userprofile.search_indexes import UserProfileIndex
from common.api_helper import get_objects_paginated
from common.push_message import *

logger = logging.getLogger('meanwise_backend.%s' % __name__)


class ProfessionListView(APIView):
    """
    Profession apis

    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        professions = Profession.objects.all()
        paginator = Paginator(
            professions, settings.REST_FRAMEWORK['PAGE_SIZE'])
        page = request.GET.get('page', 1)

        try:
            professions = paginator.page(page)
        except PageNotAnInteger:
            professions = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of
            # results.
            professions = paginator.page(paginator.num_pages)
        serializer = ProfessionSerializer(professions, many=True)
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "data": serializer.data,
                    'num_pages': professions.paginator.num_pages
                }
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = ProfessionSerializer(data=request.data)
        if serializer.is_valid():
            profession = serializer.save()
            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": "successfully added skill"
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "status": "failed",
                "error": serializer.errors,
                "results": "Failed to add skill"
            },
            status=status.HTTP_400_BAD_REQUEST
        )


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
            # If page is out of range (e.g. 9999), deliver last page of
            # results.
            skills = paginator.page(paginator.num_pages)
        serializer = SkillSerializer(skills, many=True)
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "data": serializer.data,
                    'num_pages': skills.paginator.num_pages
                }
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = SkillSerializer(data=request.data)
        if serializer.is_valid():
            skill = serializer.save()
            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": "successfully added profession"
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "status": "failed",
                "error": serializer.errors,
                "results": "Failed to add profession"
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class InterestListView(APIView):
    """
    Interest apis

    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        interests = Interest.objects.all()

        if not request.user.is_anonymous:
            def sort_by_relevance(interest):
                try:
                    relevance = UserInterestRelevance.objects.get(
                        interest=interest, user=request.user)
                except UserInterestRelevance.DoesNotExist:
                    return 0
                return math.log1p(relevance.old_views + relevance.weekly_views)

            interests = sorted(interests, key=sort_by_relevance, reverse=True)

        serializer = InterestSerializer(interests, many=True)
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "data": serializer.data,
                    'num_pages': 1
                }
            },
            status=status.HTTP_200_OK
        )


class UserProfileList(APIView):
    """
    List all Users .
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        userprofiles = UserProfile.objects.all()

        serializer = UserProfileSerializer(
            userprofiles, many=True, context={'request': request})
        return Response(
            {
                "status": "success",
                "error": "",
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )


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
            return Response(
                {
                    "status": "failed",
                    "error": "User not found",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except UserProfile.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "error": "UserProfile not found",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return userprofile

    def get(self, request, user_id):
        userprofile = self.get_object(user_id)
        serializer = UserProfileSerializer(
            userprofile, context={'request': request, 'user_id': user_id})
        return Response(
            {
                "status": "success",
                "error": "test",
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def patch(self, request, user_id):
        data = request.data
        userprofile = self.get_object(user_id)

        if int(user_id) != request.user.id:
            raise PermissionDenied(
                "You cannot change profile for another user")

        serialized_up = UserProfileUpdateSerializer(
            userprofile, data=data, partial=True, context={'request': request})
        if serialized_up.is_valid():
            up = serialized_up.save()
            # handle username
            user_username = None
            if serialized_up.validated_data.get('user_username', None):
                user_username = serialized_up.validated_data.pop(
                    'user_username')
                up.user.username = user_username
                up.user.save()
            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": serialized_up.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "status": "failed",
                "error": serialized_up.errors,
                "results": ""
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class LoggedInUserProfile(APIView):
    """
    Edit a userprofile instance.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, user_id):
        try:
            userprofile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "error": "UserProfile not found",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return userprofile

    def get(self, request):
        userprofile = request.user.userprofile
        serializer = UserProfileSerializer(userprofile)
        return Response(
            {
                "status": "success",
                "error": "",
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )


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


@permission_classes([TokenAuthentication, ])
class RequestInterest(APIView):

    def post(self, request):
        logger.info(
            "Request for interest - POST - RequestInterest [API / views.py /")
        try:
            interest_name = request.data.get('name', None)
            description = request.data.get('description', None)
            already_exists = False
            try:
                interest = Interest.objects.get(name=interest_name)
            except Interest.DoesNotExist:
                create_one = True
            except Exception as e:
                return Response({"error": sstr(e)}, status.HTTP_400_BAD_REQUEST)
            if not already_exists:
                if interest.published:
                    return Response(
                        {
                            "message": "Interest with name already published"
                        },
                        status.HTTP_200_OK
                    )

                else:
                    interest.vote_count += 1
                    interest.save()
                    return Response({"message": "Succesfully submitted"}, status.HTTP_200_OK)
            else:
                interest = Interest.objects.create(name=interest_name, slug=slugify(
                    name), description=description, vote_count=1)
                return Response({"message": "Succesfully submitted"}, status.HTTP_200_OK)

        except requests.RequestException as e:
            logger.error("Request Interest - POST - Exception: " +
                         e.message + " [API / views.py /")
            return Response({"error": str(e)}, status.HTTP_400_BAD_REQUEST)


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
            return Response(
                {
                    "status": "failed",
                    "error": "User not found",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return user

    def post(self, request, user_id):
        self.object = self.get_object(user_id)
        serializer = ChangePasswordSerializer(data=request.data)

        if int(user_id) != request.user.id:
            raise PermissionDenied(
                "You cannot change password for other users")

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {
                        "status": "failed",
                        "error": "Wrong old password",
                        "results": ""
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # check new password
            errors = dict()
            try:
                validators.validate_password(
                    password=serializer.data.get("new_password"), user=User)
            except exceptions.ValidationError as e:
                errors['password'] = list(e.messages)
            if errors:
                return Response(
                    {
                        "status": "failed",
                        "error": errors,
                        "results": ""
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": "successfully changes password"
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    """
    An endpoint for forgotten password.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        serializer = ForgotPasswordSerializer(data=data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {
                        "status": "failed",
                        "error": "User not found",
                        "results": ""
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # set_password also hashes the password that the user will get
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            try:
                subject, from_email, to = 'New password', 'no-reply@meanwise.com', email
                text_content = ("Hey,\n\n"
                                "Uh oh! Looks like you forgot your password. Here’s a temporary password:\n\n" +
                                "%s" % (str(password),) +
                                "\n\n"
                                "Use it to sign in, go to settings, and set your new password. Happy Posting!\n\n"
                                "Cheers,\n\n"
                                "Meanwise"
                                )
                html_content = ("Hey,<br/>\n\n"
                                "<p>Uh oh! Looks like you forgot your password. Here’s a temporary password:</p><br/>\n\n" +
                                "%s" % (str(password),) +
                                "<br/><br/>\n\n"
                                "<p>Use it to sign in, go to settings, and set your new password. Happy Posting!</p><br/>\n\n"
                                "Cheers,<br/>\n\n"
                                "Meanwise"
                                )
                msg = EmailMultiAlternatives(
                    subject, text_content, from_email, [to])
                html_content = ("Hey,<br/>\n\n"
                                "<p>Uh oh! Looks like you forgot your password. Here’s a temporary password:</p><br/>\n\n" +
                                "%s" % (str(password),) +
                                "<br/><br/>\n\n"
                                "<p>Use it to sign in, go to settings, and set your new password. Happy Posting!</p><br/>\n\n"
                                "Cheers,<br/>\n\n"
                                "Meanwise"
                                )
                msg = EmailMultiAlternatives(
                    subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                logger.error(e)
                return Response(
                    {
                        "status": "failed",
                        "error": "Could not email the new password",
                        "results": ""
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": "Successfully sent email with new password"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "status": "failed",
                "error": serializer.errors,
                "results": ""
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ValidateInviteCodeView(APIView):
    """
    An endpoint to validate invite code.
    """
    model = InviteGroup
    permission_classes = (AllowAny,)

    def post(self, request):
        invite_code = request.data.get('invite_code', '')
        if not invite_code:
            return Response(
                {
                    "status": "failed",
                    "error": "Invite code not provided",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            invite_group = InviteGroup.objects.get(invite_code=invite_code)
        except InviteGroup.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "error": "Invite Group not found",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        limit_exceeded = False
        if invite_group.count > invite_group.max_invites:
            limit_exceeded = True
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "limit_exceeded": limit_exceeded
                }
            },
            status=status.HTTP_200_OK
        )


class SetInviteCodeView(APIView):
    """
    User can set their Invite code through this API. Once set, it cannot be changed.
    """

    model = InviteGroup
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def put(self, request):
        user = request.user
        invite_code = request.data.get('invite_code', None)

        if not invite_code:
            return Response(
                {
                    "status": "failed",
                    "error": "Invite code not provided",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            invite_group = InviteGroup.objects.get(invite_code=invite_code)
        except InviteGroup.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "error": "Invite Group not found",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.userprofile.user_type == UserProfile.USERTYPE_INVITED or InviteGroup.users.through.objects.filter(user=user).count() > 0:
            return Response(
                {
                    "status": "failed",
                    "error": "You are already in an Invite Group",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if invite_group.count > invite_group.max_invites:
            return Response(
                {
                    "status": "failed",
                    "error": "Invite Group limit exceeded",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        invite_group.count += 1
        invite_group.save()
        invite_group.users.add(user)

        user.userprofile.user_type = UserProfile.USERTYPE_INVITED
        user.userprofile.save()

        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "message": "You are now in Invite Group %s" % invite_code
                }
            },
            status=status.HTTP_200_OK
        )


class UserProfileHSSerializer(HaystackSerializer):
    class Meta:
        index_classes = [UserProfileIndex]
        fields = [
            "text", "id", "first_name", "last_name", "username", "skills_text"
        ]


class UserProfileSearchView(HaystackViewSet):
    index_models = [UserProfile]
    serializer_class = UserProfileSearchSerializer
    filter_backends = [HaystackAutocompleteFilter]

    def filter_queryset(self, *args, **kwargs):
        queryset = super(UserProfileSearchView, self).filter_queryset(
            self.get_queryset())
        return queryset.order_by('-_score')


class ProfessionSearchView(HaystackViewSet):
    index_models = [Profession]
    serializer_class = ProfessionSearchSerializer
    filter_backends = [HaystackAutocompleteFilter]

    def filter_queryset(self, *args, **kwargs):
        queryset = super().filter_queryset(self.get_queryset())
        return queryset.order_by('text')


class SkillSearchView(HaystackViewSet):
    index_models = [Skill]
    serializer_class = SkillSearchSerializer
    filter_backends = [HaystackAutocompleteFilter]

    def filter_queryset(self, *args, **kwargs):
        queryset = super().filter_queryset(self.get_queryset())
        return queryset.order_by('text')


class UserMentionAutoComplete(HaystackViewSet):
    index_models = [UserProfile]
    serializer_class = UserMentionSerializer
    filter_backends = [HaystackAutocompleteFilter]

    def filter_queryset(self, *args, **kwargs):
        queryset = super(UserMentionAutoComplete, self).filter_queryset(
            self.get_queryset())

        return queryset.order_by('id')


class InfluencersListView(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        interest_name = request.query_params.get('interest_name', None)
        after = request.query_params.get('after', None)
        before = request.query_params.get('before', None)
        item_count = int(request.query_params.get('item_count', 30))
        section = int(request.query_params.get('section', 1))
        if after:
            after = datetime.datetime.fromtimestamp(float(after) / 1000)
        if before:
            before = datetime.datetime.fromtimestamp(float(before) / 1000)
        if item_count > 30:
            raise Exception("item_count greater than 30 is not allowed.")

        functions = []
        filters = []

        interest_names = list(request.user.userprofile.interests.all()
                              .values_list('name', flat=True))
        if interest_name:
            filters.append(query.Q('bool', should=[
                query.Q('match', interests_weekly=interest_name),
                query.Q('match', interests_overall=interest_name)
            ]))
        else:
            filters.append(query.Q('bool', should=[
                query.Q('match', interests_weekly=','.join(interest_names)),
                query.Q('match', interests_overall=','.join(interest_names))
            ]))

        functions.append(query.SF('field_value_factor',
                                  field='popularity_weekly',
                                  modifier='log1p',
                                  weight=5))
        functions.append(query.SF('field_value_factor',
                                  field='popularity_overall',
                                  modifier='log1p',
                                  weight=1))
        functions.append(query.SF('field_value_factor',
                                  field='friends',
                                  modifier='log1p',
                                  weight=2))

        s = Influencer.search()
        q = query.Q(
            'function_score',
            query=query.Q('bool', filter=filters),
            functions=functions,
            score_mode='sum',
            boost_mode='sum'
        )
        s = s.query(q)
        logger.info(s.to_dict())
        offset = (section - 1) * item_count
        s = s[offset:offset + item_count]

        results = s.execute()
        ids = [r.meta.id for r in results]
        logger.info(ids)
        userprofiles = UserProfile.objects.filter(user__in=ids)
        id_dict = {u.user.id: u for u in userprofiles}
        logger.info(id_dict)
        userprofiles = [id_dict[int(id)] for id in ids]

        serializer = UserProfileSerializer(userprofiles, many=True, context={'request': request})

        return Response({
            'status': 'success',
            'error': None,
            'results': serializer.data
        })


class UserFriendView(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        """
        List all friends for user (user_id)
        """

        status = request.GET.get("status")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(
                "UserFriend - GET - User not found [api / views.py /")
            return Response(
                {
                    "status": "failed",
                    "error": "User with id does not exist",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            up = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            logger.error("UserFriend - GET - user profile not found [api / views.py /")
            return Response(
                {
                    "status": "failed",
                    "error": "Userprofile with id does not exist",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if status.lower() == "pending":
            friend_requests_received = UserFriend.objects.requests(user=user)
            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": {
                        "data": FriendRequestSerializer(friend_requests_received, many=True).data,
                        "num_pages": num_pages
                    }
                },
                status=status.HTTP_200_OK
            )

        user_friends = UserFriend.objects.friends(user)

        user_friends_profiles = []

        for userfriend in user_friends:
            try:
                user_friends_profiles.append(UserProfile.objects.get(user=userfriend).id)
            except UserProfile.DoesNotExist:
                pass

        page = request.GET.get('page')
        page_size = request.GET.get('page_size')

        user_friends_profiles, has_next_page, num_pages = get_objects_paginated(
            user_friends_profiles, page, page_size)
        serialized_friends_list = UserProfileSerializer(UserProfile.objects.filter(
            id__in=user_friends_profiles),
            many=True, context={'request': request, 'user_id': user_id})
        friend_requests_sent = UserFriend.objects.sent_requests(user=user)
        friend_requests_received = UserFriend.objects.requests(user=user)

        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "data": serialized_friends_list.data,
                    "sent_requests": FriendRequestSerializer(friend_requests_sent, many=True).data,
                    "received_requests": FriendRequestSerializer(friend_requests_received, many=True).data,
                    "num_pages": num_pages
                }
            },
            status=status.HTTP_200_OK
        )

    def post(self, request, user_id):
        """
        View for accepting and rejecting FriendList
        """

        logger.info("UserFriend - POST [API / views.py /")
        friend_id = request.data.get('friend_id', None)

        if not friend_id or (int(friend_id) != request.user.id and int(user_id) != request.user.id):
            raise PermissionDenied(
                "You can only send friend request as yourself")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(
                "UserFriend - GET - User not found [api / views.py /")
            return Response(
                {
                    "status": "failed",
                    "error": "User with id does not exist",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            up = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            logger.error("UserProfile - GET - user profile not found [api / views.py /")
            return Response(
                {
                    "status": "failed",
                    "error": "Userprofile with id does not exist",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        friend_status = request.data.get('status', None)

        try:
            friend_user = User.objects.get(id=int(friend_id))
        except User.DoesNotExist:
            logger.error(
                "UserFriend - POST - friend User not found [api / views.py /")
            return Response(
                {
                    "status": "failed",
                    "error": "friend User with id does not exist",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            friend_profile = UserProfile.objects.get(user=friend_user)
        except UserProfile.DoesNotExist:
            logger.error(
                "UserFriend - POST - friend User not found [api / views.py /")
            return Response(
                {
                    "status": "failed",
                    "error": "friend UserProfile does not exist",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # try:
        #     check_friendship = UserFriend.objects.get(user=user, friend=friend_user)
        # except UserFriend.DoesNotExist:
        #     check_friendship = None
        #     pass

        # if check_friendship:
        #     logger.info(
        #         "UserFriend - POST - Finished [API / views.py /")
        #     return Response(
        #         {
        #             "status": "success",
        #             "error": "",
        #             "results": "Already friends"
        #         },
        #         status=status.HTTP_201_CREATED
        #     )

        try:
            friend_request = FriendRequest.objects.get(user=friend_user, friend=user)
        except FriendRequest.DoesNotExist:
            friend_request = None
            pass

        if friend_request:
            allow = True if request.user.id != friend_request.user.id else False

        if friend_status.lower() == "pending":
            UserFriend.objects.add_friend(
                user,
                friend_user
            )

            notification = Notification.objects.create(
                receiver=friend_user,
                notification_type=Notification.TYPE_FRIEND_REQUEST_RECEIVED)
            # send push notification
            devices = find_user_devices(friend_user.id)
            message_payload = {
                'p': '',
                'u': str(friend_user.id),
                't': 'a',
                'message': (
                    str(user.userprofile.first_name) + " " +
                    str(user.userprofile.last_name) + " has sent you a friend request."
                )
            }
            for device in devices:
                send_message_device(device, message_payload)

            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": "Successfully added friend request."
                },
                status=status.HTTP_201_CREATED
            )

        if friend_status.lower() == "accepted":
            print("called")
            if not friend_request:
                print("Step 2")
                try:
                    friends = UserFriend.objects.get(user=user, friend=friend_user)
                except UserFriend.DoesNotExist:
                    friends = None
                    pass

                if friends:
                    logger.info(
                        "UserFriend - POST - Finished [API / views.py /")
                    return Response(
                        {
                            "status": "success",
                            "error": "",
                            "results": "Already friends"
                        },
                        status=status.HTTP_201_CREATED
                    )

                else:
                    logger.error(
                        "UserFriend - POST - Userfriend not found [api / views.py /")
                    return Response(
                        {
                            "status": "failed",
                            "error": "Friend record with ids does not exist",
                            "results": ""
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            elif friend_request and allow:
                # accept a friend request
                friend_request.accept()
                friends = UserFriend.objects.get(user=user, friend=friend_user)
                notification = Notification.objects.create(
                    receiver=friend_user,
                    notification_type=Notification.TYPE_FRIEND_REQUEST_ACCEPTED,
                    user_friend=friends)
                # send push notification
                devices = find_user_devices(friend_user.id)
                message_payload = {
                    'p': '',
                    'u': str(friend_user.id),
                    't': 'a',
                    'message': (
                        str(user.userprofile.first_name) + " " +
                        str(user.userprofile.last_name) + " accepted friend request."
                    )
                }
                for device in devices:
                    send_message_device(device, message_payload)
                logger.info(
                    "UserFriend - POST - Finished [API / views.py /")
                return Response(
                    {
                        "status": "success",
                        "error": "",
                        "results": "Successfully accepted."
                    },
                    status=status.HTTP_201_CREATED
                )

            elif not allow:
                print("permission denied bitch")
                raise PermissionDenied("You cannot accept the request you sent to other user.")

        elif friend_status.lower() == "rejected":

            if not friend_request:
                try:
                    friends = UserFriend.objects.get(user=user, friend=friend_user)
                except UserFriend.DoesNotExist:
                    friends = None
                    pass

                if friends:
                    logger.info(
                        "UserFriend - POST - Finished [API / views.py /")
                    return Response(
                        {
                            "status": "success",
                            "error": "",
                            "results": "Already friends"
                        },
                        status=status.HTTP_201_CREATED
                    )

                else:
                    logger.error(
                        "UserFriend - POST - Userfriend not found [api / views.py /")
                    return Response(
                        {
                            "status": "failed",
                            "error": "Friend record with ids does not exist",
                            "results": ""
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            elif friend_request and allow:
                friend_request.reject()
                logger.info(
                    "FriendsRequest - POST - Finished [API / views.py /")
                return Response(
                    {
                        "status": "success",
                        "error": "",
                        "results": "Successfully rejected."
                    },
                    status=status.HTTP_201_CREATED
                )

            elif not allow:
                raise PermissionDenied("You cannot reject the request you sent to other user.")

        logger.info("UserFriend - POST - Finished [API / views.py /")
        return Response(
            {
                "status": "failed",
                "error": "Unknown",
                "results": "Could not add friend"
            },
            status=status.HTTP_400_BAD_REQUEST
        )


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

        if int(user_id) != request.user.id:
            raise PermissionDenied("You cannot remove friend for another user")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(
                "RemoveFriend - Post - User not found [api / views.py /")
            return Response(
                {
                    "status": "failed",
                    "error": "User with id does not exist",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        friend_id = request.data.get('friend_id', None)

        try:
            friend_user = User.objects.get(id=int(friend_id))
        except User.DoesNotExist:
            logger.error(
                "Removefriend - POST - friend User not found [api / views.py /")
            return Response(
                {
                    "status": "failed",
                    "error": "friend User with id does not exist",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            friend_request = FriendRequest.objects.get(user=user, friend=friend_user)
        except FriendRequest.DoesNotExist:
            friend_request = None

        if friend_request:
            logger.error(
                "Removefriend - POST - FriendRequest found [api / views.py /")
            return Response(
                {
                    "status": "failed",
                    "error": "Users are not friends",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            friends = UserFriend.objects.get(user=user, friend=friend_user)
        except UserFriend.DoesNotExist:
            friends = None
            pass

        if not friends:
            logger.info(
                "RemoveFriend - POST - Finished [API / views.py /")
            return Response(
                {
                    "status": "failed",
                    "error": "Users are not friends",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        UserFriend.objects.remove_friend(user=user, friend=friend_user)

        logger.info("Removelist - POST - Finished [API / views.py /")
        return Response(
            {
                "status": "success",
                "error": "",
                "results": "successfully removed friend"
            },
            status=status.HTTP_201_CREATED
        )
