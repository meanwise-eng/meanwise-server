import json
import datetime
import urllib
import arrow
import math
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F, When, Case, IntegerField, Count, Subquery, OuterRef, Value, Sum
from django.db.models.functions import Coalesce
from django.utils.datastructures import MultiValueDictKeyError
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.db.models.signals import post_delete
import logging
import operator
from functools import reduce

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import authentication, permissions

from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet

from taggit.models import Tag

from userprofile.serializers import UserProfileSerializer

from post.permissions import IsOwnerOrReadOnly

from django.contrib.contenttypes.models import ContentType
from follow.models import Follow
from brands.models import Brand
from college.models import College

from post.models import *
from post.serializers import *
from userprofile.models import UserFriend, Interest, UserInterestRelevance
from mnotifications.models import Notification
from credits.models import Credits, Critic

from elasticsearch_dsl import query
from post.search_indexes import PostIndex
from common.api_helper import get_objects_paginated, TimeBasedPaginator, NormalPaginator,\
    build_absolute_uri
from post.documents import PostDocument

from common.push_message import *

post_qs = Post.objects.filter(is_deleted=False).filter(
    Q(story__isnull=True) | Q(story_index=1)).order_by('-created_on')
logger = logging.getLogger('meanwise_backend.%s' % __name__)


class UserPostList(APIView):
    """
    List all User posts, or create a new User post.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def get(self, request, user_id):
        posts = post_qs.filter(poster__id=user_id)

        paginator = TimeBasedPaginator(posts, request)

        serializer = PostSerializer(
            paginator.page(), many=True, context={'request': request})
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "data": serializer.data,
                    "num_pages": paginator.total_pages
                },
                "forward": paginator.next_url,
                "backward": paginator.prev_url,
                "total": paginator.total
            },
            status=status.HTTP_200_OK
        )

    @transaction.atomic()
    def post(self, request, user_id):
        data = request.data

        if int(user_id) != int(request.user.id):
            raise PermissionDenied("You cannot create a post as another user")
        user = User.objects.get(pk=user_id)

        serializer = PostSaveSerializer(data=data)
        if serializer.is_valid():
            # handle topics
            topic_names = None
            if serializer.validated_data.get('topic_names', None):
                topic_names = serializer.validated_data.pop('topic_names')
            ts = []
            if 'tags' in serializer.validated_data:
                if serializer.validated_data['tags']:
                    ts = serializer.validated_data.pop('tags')
            post = serializer.save(poster=request.user)
            if topic_names:
                for topic in topic_names:
                    try:
                        t = Topic.objects.get(text=topic)
                    except Topic.DoesNotExist:
                        t = Topic.objects.create(text=topic)
                    post.topics.add(t)

            mentioned_users = serializer.validated_data.get('mentioned_users')
            logger.info(mentioned_users)
            if type(mentioned_users) == str:
                mentioned_users = ast.literal_eval(mentioned_users)
            if len(mentioned_users) > 0 and type(mentioned_users[0]) == str and mentioned_users[0].find('[') != -1:
                mentioned_users = ast.literal_eval(mentioned_users)
            if len(mentioned_users):
                for i in range(len(mentioned_users)):
                    try:
                        m = User.objects.get(pk=mentioned_users[i].id)
                    except User.DoesNotExist:
                        pass
                    post.mentioned_users.add(m)

                    # Add notification
                    up = request.user.userprofile
                    notification = Notification.objects.create(
                        receiver=m,
                        notification_type=Notification.TYPE_POST_MENTIONED_USER,
                        data={
                            'post_mentioned_user': m.id,
                            'mentioned_by': int(user_id),
                            'post_id': post.id
                        },
                        post=post,
                        profile_photo_thumbnail=up.profile_photo_thumbnail.url,
                        title='%s %s' % (up.first_name, up.last_name),
                        message='Mentioned you in a post',
                        thumbnail=post.post_thumbnail().url if post.post_thumbnail() else None,
                        datetime=datetime.datetime.now())
                    # send push notification
                    devices = find_user_devices(mentioned_users[i].id)
                    message_payload = {
                        'p': str(post.id),
                        'u': str(mentioned_users[i].id),
                        't': 'l',
                        'message': (str(
                            user.userprofile.first_name) + " " + str(user.userprofile.last_name) + "has mentioned you in a post"
                        )
                    }

                    for device in devices:
                        try:
                            send_message_device(device, message_payload)
                        except Exception as e:
                            logger.error(e)

            if post.parent is not None and post.parent.parent is not None:
                raise Exception("Parent post should not be a child post.")

            if post.parent:
                try:
                    story = Story.objects.get(main_post=post.parent)
                    post.story = story
                    post.story_index = story.posts.count() + 1
                except Story.DoesNotExist:
                    story = Story()
                    story.main_post = post.parent
                    story.save()
                    post.parent.story = story
                    post.parent.story_index = 1
                    post.story = story
                    post.story_index = 2
                    post.parent.save()
                post.save()
            # handle tags
            for t in ts:
                post.tags.add(t)

            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": {
                        "message": "Successfully created post"
                    }
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "status": "failed",
                "error": serializer.errors,
                "results": ""
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class UserPostDetail(APIView):
    """
    Delete a post instance.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrReadOnly,)

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk, is_deleted=False)
        except Post.DoesNotExist:
            raise Http404

    def delete(self, request, user_id, post_id):
        post = self.get_object(post_id)
        post.is_deleted = True

        if post.story and post.story_index == 1:
            post.story.is_deleted = True
            post.story.posts.update(is_deleted=True)
            post.story.save()

        post.save()
        post_delete.send(Post, instance=post)
        return Response(
            {
                "status": "success",
                "error": "",
                "results": "Succesfully deleted."
            },
            status=status.HTTP_202_ACCEPTED
        )


class PostDetails(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    def get_object(self, pk):
        post = self.get_post(pk)
        self.check_object_permissions(self.request, post)

        return post

    def get_post(self, pk):
        try:
            return Post.objects.get(pk=pk, is_deleted=False)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, post_id):
        post = self.get_post(post_id)

        serializer = PostSerializer(post, context={'request': request})

        return Response(
            {
                "status": "success",
                "error": None,
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def patch(self, request, post_id):
        data = request.data
        post = self.get_object(post_id)

        serializer = PostUpdateSerializer(post, data=data, partial=True,
                                          context={'request': request})
        if not serializer.is_valid():
            return Response(
                {
                    "status": "failed",
                    "error": serializer.errors,
                    "results": None
                }
            )

        serializer.save()

        return Response(
            {
                "status": "success",
                "error": None,
                "results": {
                    "message": "Post successfully updated."
                }
            }
        )


class UserFriendsPostList(APIView):
    """
    List all User's friends' posts.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        try:
            friends_ids = UserFriend.objects.filter(
                user__id=user_id).values_list('friend__id', flat=True)
            posts = post_qs.filter(Q(story__isnull=True) | Q(story_index=1))
            serializer = PostSerializer(
                posts, many=True, context={'request': request})
            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": "failed",
                    "error": str(e),
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class UserInterestsPostList(APIView):
    """
    List all User's interests based posts.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        try:
            try:
                userprofile = UserProfile.objects.get(user__id=user_id)
            except UserProfile.DoesNotExist:
                return Response(
                    {
                        "status": "failed",
                        "error": "Error fetching userprofile/interests for user.",
                        "results": ""
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            interests_ids = userprofile.interests.all().values_list('id', flat=True)
            posts = post_qs.filter(interest__id__in=interests_ids)
            serializer = PostSerializer(
                posts, many=True, context={'request': request})
            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": "failed",
                    "error": str(e),
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class StoryDetail(APIView):
    """
    Get the details of the story. Basically it's just a list of the posts.
    """

    def get_object(self, pk):
        try:
            return Story.objects.get(pk=pk, is_deleted=False)
        except Story.DoesNotExist:
            raise Http404

    def get(self, request, story_id, format=None):
        story = self.get_object(story_id)
        serializer = StorySerializer(story, context={'request': request})
        return Response(
            {
                "status": "success",
                "error": "",
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )


class UserHomeFeed(APIView):
    """
    User home feed - comprising 1. User's post 2. User's friend post 3. User's interest based post.

    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        try:
            friends_ids = UserFriend.objects.filter(
                user__id=user_id).values_list('friend__id', flat=True)
            try:
                userprofile = UserProfile.objects.get(user__id=user_id)
            except UserProfile.DoesNotExist:
                return Response(
                    {
                        "status": "failed",
                        "error": "Error fetching userprofile/interests for user.",
                        "results": ""
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            interests_ids = userprofile.interests.all().values_list('id', flat=True)
            home_feed_posts = post_qs.filter(Q(poster__id__in=friends_ids) | Q(
                interest__id__in=interests_ids) | Q(poster__id=user_id))

            # # Sorting by skills
            # skills_list = userprofile.skills_list
            # topics_subq = Topic.objects.filter(post=OuterRef('pk'))
            # topic_wheres = []
            # if len(skills_list) > 0:
            #     for skill in skills_list:
            #         topic_wheres.append(Q(text__iexact=skill))
            #     topics_subq = topics_subq.filter(reduce(operator.or_, topic_wheres))
            # else:
            #     topics_subq = topics_subq.filter(text='')
            # topics_subq = topics_subq.annotate(count=Count('pk')).values('count')[:1]

            # content_type = ContentType.objects.get_for_model(Post)
            # tags_subq = Tag.objects.filter(taggit_taggeditem_items__content_type=content_type, post=OuterRef('pk'))
            # tag_wheres = []
            # if len(skills_list) > 0:
            #     for skill in skills_list:
            #         tag_wheres.append(Q(name__iexact=skill))
            #     tags_subq = tags_subq.filter(reduce(operator.or_, tag_wheres))
            # else:
            #     tags_subq = tags_subq.filter(name=Value(''))
            # tags_subq = tags_subq.annotate(tag_count=Count('pk')).values('tag_count')[:1]

            # interests_whens = [ When(interest__id__in=interests_ids, then=1) ]
            # home_feed_posts = home_feed_posts.annotate(
            #     relevance=Coalesce(Subquery(topics_subq, output_field=IntegerField()), 0) +
            #         Coalesce(Subquery(tags_subq, output_field=IntegerField()), 0) +
            #         Case(
            #             *interests_whens,
            #             default=0,
            #             output_field=IntegerField()
            #         )
            # ).order_by(F('relevance').desc(), '-created_on')

            page = request.GET.get('page')
            page_size = request.GET.get('page_size')
            home_feed_posts, has_next_page, num_pages = get_objects_paginated(
                home_feed_posts, page, page_size)
            serializer_context = {
                'request': request,
            }
            serializer = PostSerializer(
                home_feed_posts, many=True, context=serializer_context)
            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": {
                        "data": serializer.data,
                        "num_pages": num_pages
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.exception(e)

            return Response(
                {
                    "status": "failed",
                    "error": str(e),
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

            return Response(
                {
                    "status": "failed",
                    "error": str(e),
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class PublicFeed(APIView):

    def get(self, request):
        posts = post_qs.all()[:20]
        serializer = PostSerializer(
            posts, many=True, context={'request': request})
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "data": serializer.data
                }
            },
            status=status.HTTP_200_OK
        )


class PostViewSet(viewsets.ModelViewSet):
    """
    Post apis

    """
    queryset = Post.objects.all().order_by('-created_on')
    serializer_class = PostSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,
                          IsOwnerOrReadOnly,)
    fields = ('id', 'interest', 'image', 'video', 'text', 'poster',
              'tags', 'liked_by', 'is_deleted', 'created_on', 'modified_on')

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.save()
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPostLike(APIView):
    """
    User likes a post instance.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404

    def post(self, request, user_id, post_id):
        post = self.get_object(post_id)
        user = User.objects.get(id=user_id)

        if user != request.user:
            raise PermissionDenied("You can only like a post as yourself")

        if user not in post.liked_by.all():
            skills = list(post.topics.all().values_list('text', flat=True))
            critic = Critic.objects.create(from_user_id=user.id, to_user_id=post.poster.id,
                                           post_id=post.id, user_credits=0, rating=3,
                                           skills=skills, created_on=datetime.datetime.now())

            for skill in (skills + ['overall']):
                try:
                    credits = Credits.objects.get(user_id=post.poster.id, skill=skill)
                except Credits.DoesNotExist:
                    credits = Credits.objects.create(user_id=post.poster.id, skill=skill, credits=0)

                credits.credits += 1
                credits.save()

        post.liked_by.add(user)

        if post.poster.id != request.user.id:
            # Add notification
            up = user.userprofile
            notification = Notification.objects.create(
                receiver=post.poster,
                notification_type=Notification.TYPE_LIKED_POST,
                post=post, post_liked_by=user,
                profile_photo_thumbnail=up.profile_photo_thumbnail.url,
                title=up.fullname(),
                message='Liked your post',
                datetime=datetime.datetime.now(),
                thumbnail=post.post_thumbnail().url if post.post_thumbnail() else None,
                data={'liked_by': user.id, 'post_id': post.id})
            # send push notification
            devices = find_user_devices(post.poster.id)
            message_payload = {
                'p': str(post.id),
                'u': str(post.poster.id),
                't': 'l',
                'message': (
                    str(user.userprofile.first_name) + " " +
                    str(user.userprofile.last_name) + " liked your post"
                )
            }

            for device in devices:
                send_message_device(device, message_payload)
        return Response(
            {
                "status": "success",
                "error": "",
                "results": "Succesfully liked."
            },
            status=status.HTTP_202_ACCEPTED
        )


class UserPostUnLike(APIView):
    """
    User unlikes a post instance.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404

    def post(self, request, user_id, post_id):
        post = self.get_object(post_id)
        user = User.objects.get(id=user_id)

        if user != request.user:
            raise PermissionDenied("You cannot create a post as another user")

        if user in post.liked_by.all():
            post.liked_by.remove(user)

            critic = Critic.objects.filter(from_user_id=user.id, to_user_id=post.poster.id,
                                           post_id=post.id).delete()

            skills = list(post.topics.all().values_list('text', flat=True))
            for skill in (skills + ['overall']):
                try:
                    credits = Credits.objects.get(user_id=post.poster.id, skill=skill)
                    credits.credits -= 1
                    credits.save()
                except Credits.DoesNotExist:
                    pass
            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": "Succesfully unliked."
                },
                status=status.HTTP_202_ACCEPTED
            )
        else:
            return Response(
                {
                    "status": "failed",
                    "error": "User not in liked list",
                    "results": ""
                },
                status=status.HTTP_202_ACCEPTED
            )


class PostLikes(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_post(self, post_id):
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, post_id):
        post = self.get_post(post_id)

        page = request.GET.get('page')
        page_size = request.GET.get('page_size')

        liked_by = UserProfile.objects.filter(user__in=post.liked_by.all())\
            .order_by('first_name', 'last_name')
        paginator = NormalPaginator(liked_by, request)

        serializer = UserProfileSerializer(
            paginator.page(), many=True, context={'request': request})
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "data": serializer.data,
                    "num_pages": paginator.total_pages
                },
                "forward": paginator.next_url,
                "backward": paginator.prev_url,
                "total": paginator.total
            },
            status=status.HTTP_200_OK
        )


class PostCommentList(APIView):
    """
    List all post related comments, or create a new User comment.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, post_id):
        comments = Comment.objects.filter(is_deleted=False).filter(
            post__id=post_id).order_by('-created_on')

        paginator = TimeBasedPaginator(comments, request)

        serializer = CommentSerializer(paginator.page(), many=True)
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "data": serializer.data,
                    "num_pages": paginator.total_pages
                },
                "forward": paginator.next_url,
                "backward": paginator.prev_url,
                "total": paginator.total
            },
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def post(self, request, post_id):
        data = request.data.copy()
        data['post'] = post_id
        serializer = CommentSaveSerializer(data=data)

        if serializer.is_valid():

            try:
                if serializer.validated_data['commented_by'] != request.user:
                    raise PermissionDenied(
                        "You can't posts comments as another user")

                comment = serializer.save()
                if comment.post.poster.id != request.user.id:
                    # Add notification
                    up = comment.commented_by.userprofile
                    notification = Notification.objects.create(
                        receiver=comment.post.poster,
                        notification_type=Notification.TYPE_COMMENTED_POST,
                        post=comment.post,
                        comment=comment,
                        profile_photo_thumbnail=up.profile_photo_thumbnail.url,
                        title=up.fullname(),
                        message='Commented on your post',
                        datetime=datetime.datetime.now(),
                        thumbnail=comment.post.post_thumbnail().url if comment.post.post_thumbnail() else None,
                        data={
                            'comment_id': comment.id,
                            'post_id': comment.post.id,
                            'commented_by': comment.commented_by.id,
                        })
                    # send push notification
                    devices = find_user_devices(comment.post.poster.id)
                    message_payload = {
                        'p': str(comment.post.id),
                        'u': str(comment.post.poster.id),
                        't': 'c',
                        'message': (
                            str(comment.commented_by.userprofile.first_name) + " " +
                            str(comment.commented_by.userprofile.last_name) + " commented on your post"
                        )
                    }

                    logger.info("No of devices to send: %s" % len(devices))
                    for device in devices:
                        logger.info("Sending notification to device: %s" % device)
                        send_message_device(device, message_payload)

                mentioned_users = serializer.validated_data.get('mentioned_users')
                logger.info(mentioned_users)
                if type(mentioned_users) == str:
                    mentioned_users = ast.literal_eval(mentioned_users)
                if mentioned_users and len(mentioned_users) > 0 and type(mentioned_users[0]) == str and mentioned_users[0].find('[') != -1:
                    mentioned_users = ast.literal_eval(mentioned_users)

                if mentioned_users and len(mentioned_users):
                    for i in range(len(mentioned_users)):
                        try:
                            m = User.objects.get(pk=mentioned_users[i].id)
                        except User.DoesNotExist:
                            pass
                        comment.mentioned_users.add(m)

                        # Add notification
                        notification = Notification.objects.create(
                            receiver=m,
                            notification_type=Notification.TYPE_COMMENT_MENTIONED_USER,
                            comment=comment,
                            post=comment.post,
                            profile_photo_thumbnail=up.profile_photo.url,
                            title=up.fullname(),
                            message='Mentioned you in a comment',
                            thumbnail=comment.post.post_thumbnail().url if comment.post.post_thumbnail() else None,
                            data={
                                'comment_mentioned_user': m.id,
                                'mentioned_by': comment.commented_by.id,
                                'comment_id': comment.id,
                                'post_id': comment.post.id,
                            })
                        # send push notification
                        devices = find_user_devices(mentioned_users[i].id)
                        message_payload = {
                            'p': str(comment.id),
                            'u': str(comment.commented_by.id),
                            't': 'l',
                            'message': (
                                str(comment.commented_by.userprofile.first_name) + " " +
                                str(comment.commented_by.userprofile.last_name) +
                                "has mentioned you in a comment"
                            )
                        }
                        for device in devices:
                            send_message_device(device, message_payload)

                return Response(
                    {
                        "status": "success",
                        "error": "",
                        "results": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as ex:
                logger.error(ex)
                return Response(
                    {
                        "status": "failed",
                        "error": "Error saving comment.",
                        "results": ""
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            {
                "status": "failed",
                "error": serializer.errors,
                "results": ""
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class PostCommentDetail(APIView):
    """
    Delete a comment instance.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrReadOnly,)

    def get_object(self, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            return comment
        except Comment.DoesNotExist:
            raise Http404

    def delete(self, request, post_id, comment_id):
        comment = self.get_object(comment_id)

        post = Post.objects.filter(id=post_id).values("poster")
        poster = list(post)[0]["poster"]

        if comment.commented_by.id != request.user.id and poster != request.user.id:
            raise PermissionDenied(
                "You cannot delete comment of someone else, if you're not the original poster")

        comment.is_deleted = True
        comment.save()

        post_delete.send(Comment, instance=comment)

        return Response(
            {
                "status": "success",
                "error": "",
                "results": "Succesfully deleted."
            },
            status=status.HTTP_202_ACCEPTED
        )


class CommentViewSet(viewsets.ModelViewSet):
    """
    Comment apis

    """
    queryset = Comment.objects.all().order_by(
        '-created_on').filter(is_deleted=False)
    serializer_class = CommentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'post', 'commented_by',
              'comment_text', 'created_on', 'modified_on', 'mentioned_users')


class ShareViewSet(viewsets.ModelViewSet):
    """
    Share apis

    """
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'post', 'messag', 'shared_by',
              'recepients', 'created_on', 'modified_on')


class AutocompleteTag(APIView):
    """
    Auto complete tags for given text
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        tag_text = request.data.get('tag', '')
        try:
            tags = Tag.objects.filter(name__istartswith=tag_text).filter(
                post__is_deleted=False).distinct().values_list('name', flat=True)
        except MultiValueDictKeyError:
            pass

        return Response(
            {
                "status": "success",
                "error": "",
                "results": tags
            },
            status=status.HTTP_201_CREATED
        )


class AutocompleteTopic(APIView):
    """
    Auto complete topics for given text
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        topic_text = request.data.get('topic', '')
        try:
            topics = Topic.objects.filter(text__istartswith=topic_text).filter(
                post__is_deleted=False).distinct().values_list('text', flat=True)
        except MultiValueDictKeyError:
            pass

        return Response(
            {
                "status": "success",
                "error": "",
                "results": topics
            },
            status=status.HTTP_201_CREATED
        )


class TrendingTopicForInterest(APIView):
    """
    Fetch top ten trending topics for an interest
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, interest_id):
        try:
            interest = Interest.objects.get(id=interest_id)
        except Interest.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "error": "Interest with given id does not Exist",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            tt = TrendingTopicsInterest.objects.get(interest=interest)
        except TrendingTopicsInterest.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "error": "Could not find relevant value in TrendingTopicsInterest.",
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "status": "success",
                "error": "",
                "results": tt.topics
            },
            status=status.HTTP_201_CREATED
        )


class TrendingTopics(APIView):
    """
    Fetch the trending topics
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        trending_topics = list(UserTopic.objects.values('topic').annotate(total_popularity=Sum('popularity')).order_by('-total_popularity')[:50].values_list('topic', flat=True))

        skills_list = request.user.userprofile.skills_list

        return Response(
            {
                "status": "success",
                "error": "",
                "results": trending_topics
            },
            status=status.HTTP_201_CREATED
        )


class PostExploreView(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request):
        search_text = request.query_params.get('search', None)
        topic_texts = request.query_params.get('topic_texts', None)
        tag_names = request.query_params.get('tag_names', None)
        is_work = request.query_params.get('is_work', None)
        if is_work is not None:
            is_work = True if is_work == 'true' else False
        user_id = request.query_params.get('user_id', None)
        geo_location = request.query_params.get('geo_location', None)
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

        items_per_page = item_count

        user = request.user
        if not user.is_anonymous:
            interest_ids = list(request.user.userprofile.interests.all().values_list('id', flat=True))
            friends_ids = list(UserFriend.objects.filter(Q(user_id=request.user.id)).all().values_list('friend_id', flat=True)) + \
                list(UserFriend.objects.filter(Q(friend_id=request.user.id)).all().values_list('user_id', flat=True))
            skills_list = request.user.userprofile.skills_list

        functions = []
        filters = []
        must = []
        if topic_texts:
            topic_texts = topic_texts.upper()
            must.append(query.Q('term', topics=topic_texts))
        if tag_names:
            must.append(query.Q('match', tags=tag_names))
        if is_work is not None:
            must.append(query.Q('term', is_work=is_work))
        if search_text:
            must.append(query.Q('match', post_document=search_text))

        if geo_location:
            functions.append(
                query.SF({'filter': query.Q('exists', field='geo_location'), 'weight': 1}))
            functions.append(query.SF('exp', geo_location={'origin': '%s,%s' % geo_location.split(
                ','), 'scale': '1km', 'decay': 0.9}, weight=1))
        if user_id:
            must.append(query.Q('term', user_id=user_id))

        now = datetime.datetime.now()
        origin = before if before else now

        if after:
            must.append(query.Q({'range': {'created_on': {'gt': after}}}))
        if before:
            must.append(query.Q({'range': {'created_on': {'lt': before}}}))
        else:
            must.append(query.Q({'range': {'created_on': {'lt': now}}}))

        # applying privacy
        if not user.is_anonymous:
            privacy_qs = []
            privacy_qs.append(query.Q('term', visible_to='Public'))
            privacy_qs.append(query.Q('bool', must=[
                query.Q('term', visible_to='Friends'),
                query.Q('terms', user_id=friends_ids)
            ]))
            privacy_qs.append(query.Q('bool', must=[
                query.Q('term', visible_to='List'),
                query.Q('term', share_list_user_ids=request.user.id)
            ]))
            must.append(query.Q('bool', should=privacy_qs))

        # overall popularity
        functions.append(query.SF('field_value_factor',
                                  field='num_likes', modifier='log1p', weight=2))
        functions.append(query.SF('field_value_factor',
                                  field='num_comments', modifier='log1p', weight=3))
        functions.append(query.SF('field_value_factor',
                                  field='num_seen', modifier='log1p', weight=1))

        # relevance to user
        if not user.is_anonymous:
            functions.append(query.SF({'filter': query.Q('terms', user_id=friends_ids), 'weight': 1}))
            functions.append(
                query.SF({'filter': query.Q('match', tags=" ".join(skills_list)), 'weight': 1}))
            functions.append(
                query.SF({'filter': query.Q('terms', topics=skills_list), 'weight': 1}))
            brand_content_type = ContentType.objects.get_for_model(Brand)
            user_content_type = ContentType.objects.get_for_model(request.user.__class__)
            brand_ids = list(Follow.objects.filter(follower_id=request.user.id,
                follower_content_type=user_content_type,
                followee_content_type=brand_content_type).values_list('followee_id', flat=True))
            functions.append(
                query.SF({'filter': query.Q('terms', brand=brand_ids), 'weight': 1}))

        s = PostDocument.search()
        q = query.Q(
            'function_score',
            query=query.Q('bool', must=must, filter=filters),
            functions=functions,
            score_mode='sum',
            boost_mode='sum'
        )
        s = s.query(q)
        s = s.sort('-created_on')
        offset = (section - 1) * item_count
        s = s[offset:offset + items_per_page]
        logger.info(s.to_dict())
        results = s.execute()
        serializer = PostDocumentSerializer(results, many=True, context={'request': request})

        query_params = dict(request.query_params)

        def get_biggest_date(date1, date2):
            if date1 > date2:
                return date1

            return date2

        def get_smallest_date(date1, date2):
            if date1 < date2:
                return date1

            return date2

        if after and results.hits.total > item_count:
            max_created_on = reduce(get_biggest_date, [result.created_on for result in results])
            min_created_on = reduce(get_smallest_date, [result.created_on for result in results])

            ps = PostDocument.search()
            must.append(query.Q({
                'range': {'created_on': {'gte': min_created_on, 'lte': max_created_on}}
            }))
            q = query.Q('bool', must=must, filter=filters)
            ps = ps.query(q)
            time_total = ps.count() - ((section - 1) * item_count)

        new_params = {}
        if after and results.hits.total > item_count:
            if time_total > item_count:
                after_date = after
                new_params['section'] = section + 1
            else:
                after_date = max_created_on
        elif before:
            if section > 1:
                before_timestamp = before
                new_params['section'] = section - 1
                after_date = None
            else:
                after_date = before
                new_params['section'] = 1
        else:
            after_date = now
            new_params['section'] = 1

        try:
            new_params['after'] = str(int(after_date.timestamp() * 1000))
        except Exception:
            pass
        try:
            new_params['before'] = str(int(before_timestamp.timestamp() * 1000))
        except Exception:
            pass

        next_url_params = {k: p[0] for k, p in query_params.copy().items()}
        if 'before' in next_url_params:
            del next_url_params['before']
        next_url_params.update(new_params)
        next_url = build_absolute_uri(
            reverse('post-explore')) + '?' + urllib.parse.urlencode(next_url_params)

        new_params = {}
        if after:
            before_timestamp = after
            new_params['section'] = 1
        elif results.hits.total > (section * item_count):
            before_timestamp = before if before else now
            new_params['section'] = section + 1
        else:
            before_timestamp = None
        if before_timestamp:
            new_params['before'] = str(int(before_timestamp.timestamp() * 1000))
            prev_url_params = {k: p[0] for k, p in query_params.copy().items()}
            if 'after' in prev_url_params:
                del prev_url_params['after']
            prev_url_params.update(new_params)
            prev_url = build_absolute_uri(
                reverse('post-explore')) + '?' + urllib.parse.urlencode(prev_url_params)
        else:
            prev_url = None

        return Response(
            {
                "status": "success",
                "error": "",
                "count": results.hits.total,
                # in haystack view next will go backwards. Deprecated. New clients should
                # use forward and backward.
                "next": prev_url,
                # in haystack view previous will go forwards. Deprecated. New clients should
                # use forward and backward.
                "previous": next_url,
                "forward": next_url,
                "backward": prev_url,
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def update_interest_relevance(self, interest_name, user):
        try:
            interest = Interest.objects.get(name=interest_name)
        except Interest.DoesNotExist:
            return

        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            relevance = UserInterestRelevance.objects.get(interest=interest, user=user)
        except UserInterestRelevance.DoesNotExist:
            relevance = UserInterestRelevance.objects.create(
                interest=interest,
                user=user,
                last_reset=now,
                weekly_views=0,
                old_views=0,
            )

        if relevance.last_reset < (now - datetime.timedelta(weeks=1)):
            decay = 0.5
            relevance.last_reset = now
            relevance.old_views = int(relevance.old_views * decay) + relevance.weekly_views
            relevance.weekly_views = 0

        relevance.weekly_views += 1

        relevance.save()


class PostExploreTrendingView(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        topic_texts = request.query_params.get('topic_texts', None)
        tag_names = request.query_params.get('tag_names', None)
        is_work = request.query_params.get('is_work', None)
        if is_work is not None:
            is_work = True if is_work == 'true' else False
        geo_location = request.query_params.get('geo_location', None)
        user_id = request.query_params.get('user_id', None)
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

        items_per_page = item_count

        friends_ids = list(UserFriend.objects.filter(Q(user_id=request.user.id)).all().values_list('friend_id', flat=True)) + \
            list(UserFriend.objects.filter(Q(friend_id=request.user.id)).all().values_list('user_id', flat=True))
        skills_list = request.user.userprofile.skills_list

        functions = []
        filters = []
        must = []
        if topic_texts:
            topic_texts = topic_texts.upper()
            must.append(query.Q('match', topics=topic_texts))
        if tag_names:
            must.append(query.Q('match', tags=tag_names))
        if is_work is not None:
            must.append(query.Q('term', is_work=is_work))
        if geo_location:
            functions.append(
                query.SF({'filter': query.Q('exists', field='geo_location'), 'weight': 1}))
            functions.append(query.SF('exp', geo_location={'origin': '%s,%s' % geo_location.split(
                ','), 'scale': '1km', 'decay': 0.9}, weight=1))
        if user_id:
            must.append(query.Q('term', user_id=user_id))

        now = datetime.datetime.now()
        origin = before if before else now

        if after:
            must.append(query.Q({'range': {'created_on': {'gt': after}}}))
        if before:
            must.append(query.Q({'range': {'created_on': {'lt': before}}}))
        else:
            must.append(query.Q({'range': {'created_on': {'lt': now}}}))

        # applying privacy
        privacy_qs = []
        privacy_qs.append(query.Q('term', visible_to='Public'))
        privacy_qs.append(query.Q('bool', must=[
            query.Q('term', visible_to='Friends'),
            query.Q('terms', user_id=friends_ids)
        ]))
        privacy_qs.append(query.Q('bool', must=[
            query.Q('term', visible_to='List'),
            query.Q('term', share_list_user_ids=request.user.id)
        ]))
        must.append(query.Q('bool', should=privacy_qs))

        # overall popularity
        functions.append(query.SF('exp', created_on={
                         'origin': origin, 'offset': '7d', 'scale': '7d', 'decay': 0.9}, weight=30))
        functions.append(query.SF('field_value_factor',
                                  field='num_likes', modifier='log1p', weight=2))
        functions.append(query.SF('field_value_factor',
                                  field='num_comments', modifier='log1p', weight=3))
        functions.append(query.SF('field_value_factor',
                                  field='num_seen', modifier='log1p', weight=1))

        # relevance to user
        functions.append(query.SF({'filter': query.Q('terms', user_id=friends_ids), 'weight': 1}))
        functions.append(
            query.SF({'filter': query.Q('match', tags=" ".join(skills_list)), 'weight': 1}))
        functions.append(
            query.SF({'filter': query.Q('terms', terms=skills_list), 'weight': 1}))
        brand_content_type = ContentType.objects.get_for_model(Brand)
        user_content_type = ContentType.objects.get_for_model(request.user.__class__)
        brand_ids = list(Follow.objects.filter(follower_id=request.user.id,
            follower_content_type=user_content_type,
            followee_content_type=brand_content_type).values_list('followee_id', flat=True))
        functions.append(
            query.SF({'filter': query.Q('terms', brand=brand_ids), 'weight': 1}))

        # manual boost
        functions.append(query.SF('exp', boost_datetime={
            'origin': origin, 'scale': '1d', 'decay': 0.1},
            weight=5))
        functions.append(query.SF('field_value_factor', field='boost_value',
                                  modifier='log1p', weight=30, missing=0))

        s = PostDocument.search()
        q = query.Q(
            'function_score',
            query=query.Q('bool', must=must, filter=filters),
            functions=functions,
            score_mode='sum',
            boost_mode='sum'
        )
        s = s.query(q)
        offset = (section - 1) * item_count
        s = s[offset:offset + items_per_page]

        results = s.execute()
        serializer = PostDocumentSerializer(results, many=True, context={'request': request})

        query_params = dict(request.query_params)

        def get_biggest_date(date1, date2):
            if date1 > date2:
                return date1

            return date2

        def get_smallest_date(date1, date2):
            if date1 < date2:
                return date1

            return date2

        if after and results.hits.total > item_count:
            max_created_on = reduce(get_biggest_date, [result.created_on for result in results])
            min_created_on = reduce(get_smallest_date, [result.created_on for result in results])

            ps = PostDocument.search()
            must.append(query.Q({
                'range': {'created_on': {'gte': min_created_on, 'lte': max_created_on}}
            }))
            q = query.Q('bool', must=must, filter=filters)
            ps = ps.query(q)
            time_total = ps.count() - ((section - 1) * item_count)

        new_params = {}
        if after and results.hits.total > item_count:
            if time_total > item_count:
                after_date = after
                new_params['section'] = section + 1
            else:
                after_date = max_created_on
        elif before:
            if section > 1:
                before_timestamp = before
                new_params['section'] = section - 1
                after_date = None
            else:
                after_date = before
                new_params['section'] = 1
        else:
            after_date = now
            new_params['section'] = 1

        try:
            new_params['after'] = str(int(after_date.timestamp() * 1000))
        except Exception:
            pass
        try:
            new_params['before'] = str(int(before_timestamp.timestamp() * 1000))
        except Exception:
            pass

        next_url_params = {k: p[0] for k, p in query_params.copy().items()}
        if 'before' in next_url_params:
            del next_url_params['before']
        next_url_params.update(new_params)
        next_url = build_absolute_uri(
            reverse('post-explore')) + '?' + urllib.parse.urlencode(next_url_params)

        new_params = {}
        if after:
            before_timestamp = after
            new_params['section'] = 1
        elif results.hits.total > (section * item_count):
            before_timestamp = before if before else now
            new_params['section'] = section + 1
        else:
            before_timestamp = None
        if before_timestamp:
            new_params['before'] = str(int(before_timestamp.timestamp() * 1000))
            prev_url_params = {k: p[0] for k, p in query_params.copy().items()}
            if 'after' in prev_url_params:
                del prev_url_params['after']
            prev_url_params.update(new_params)
            prev_url = build_absolute_uri(
                reverse('post-explore')) + '?' + urllib.parse.urlencode(prev_url_params)
        else:
            prev_url = None

        return Response(
            {
                "status": "success",
                "error": "",
                "count": results.hits.total,
                "forward": next_url,
                "backward": prev_url,
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )


class PostRelatedView(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, post_id):
        topic_texts = request.query_params.get('topic_texts', None)
        tag_names = request.query_params.get('tag_names', None)
        is_work = request.query_params.get('is_work', None)
        if is_work is not None:
            is_work = True if is_work == 'true' else False
        user_id = request.query_params.get('user_id', None)
        geo_location = request.query_params.get('geo_location', None)
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

        user = request.user

        items_per_page = item_count

        if not user.is_anonymous:
            friends_ids = list(UserFriend.objects.filter(Q(user_id=request.user.id)).all().values_list('friend_id', flat=True)) + \
                list(UserFriend.objects.filter(Q(friend_id=request.user.id)).all().values_list('user_id', flat=True))
            skills_list = request.user.userprofile.skills_list

        functions = []
        filters = []
        must = []
        must_not = []

        must_not.append(query.Q('term', _id=post_id))

        now = datetime.datetime.now()
        origin = before if before else now

        if after:
            must.append(query.Q({'range': {'created_on': {'gt': after}}}))
        if before:
            must.append(query.Q({'range': {'created_on': {'lt': before}}}))
        else:
            must.append(query.Q({'range': {'created_on': {'lt': now}}}))

        # applying privacy
        if not user.is_anonymous:
            privacy_qs = []
            privacy_qs.append(query.Q('term', visible_to='Public'))
            privacy_qs.append(query.Q('bool', must=[
                query.Q('term', visible_to='Friends'),
                query.Q('terms', user_id=friends_ids)
            ]))
            privacy_qs.append(query.Q('bool', must=[
                query.Q('term', visible_to='List'),
                query.Q('term', share_list_user_ids=request.user.id)
            ]))
            must.append(query.Q('bool', should=privacy_qs))

        # overall popularity
        functions.append(query.SF('field_value_factor',
                                  field='num_likes', modifier='log1p', weight=2))
        functions.append(query.SF('field_value_factor',
                                  field='num_comments', modifier='log1p', weight=3))
        functions.append(query.SF('field_value_factor',
                                  field='num_seen', modifier='log1p', weight=1))

        # relevance to user
        if not user.is_anonymous:
            functions.append(query.SF({'filter': query.Q('terms', user_id=friends_ids), 'weight': 1}))
            functions.append(
                query.SF({'filter': query.Q('match', tags=" ".join(skills_list)), 'weight': 1}))

        # relevance to post
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise Http404()

        post_topics = [t.text for t in post.topics.all()]
        post_tags = [t.name for t in post.tags.all()]

        functions.append(query.SF({'filter': query.Q('terms', topics=post_topics), 'weight': 10}))
        functions.append(query.SF({'filter': query.Q('terms', tags=post_tags), 'weight': 10}))

        s = PostDocument.search()
        q = query.Q(
            'function_score',
            query=query.Q('bool', must=must, filter=filters, must_not=must_not),
            functions=functions,
            score_mode='sum',
            boost_mode='sum'
        )
        s = s.query(q)
        s = s.sort('-created_on')
        offset = (section - 1) * item_count
        s = s[offset:offset + items_per_page]

        results = s.execute()
        serializer = PostDocumentSerializer(results, many=True, context={'request': request})

        query_params = dict(request.query_params)

        def get_biggest_date(date1, date2):
            if date1 > date2:
                return date1

            return date2

        def get_smallest_date(date1, date2):
            if date1 < date2:
                return date1

            return date2

        if after and results.hits.total > item_count:
            max_created_on = reduce(get_biggest_date, [result.created_on for result in results])
            min_created_on = reduce(get_smallest_date, [result.created_on for result in results])

            ps = PostDocument.search()
            must.append(query.Q({
                'range': {'created_on': {'gte': min_created_on, 'lte': max_created_on}}
            }))
            q = query.Q('bool', must=must, filter=filters)
            ps = ps.query(q)
            time_total = ps.count() - ((section - 1) * item_count)

        new_params = {}
        if after and results.hits.total > item_count:
            if time_total > item_count:
                after_date = after
                new_params['section'] = section + 1
            else:
                after_date = max_created_on
        elif before:
            if section > 1:
                before_timestamp = before
                new_params['section'] = section - 1
                after_date = None
            else:
                after_date = before
                new_params['section'] = 1
        else:
            after_date = now
            new_params['section'] = 1

        try:
            new_params['after'] = str(int(after_date.timestamp() * 1000))
        except Exception:
            pass
        try:
            new_params['before'] = str(int(before_timestamp.timestamp() * 1000))
        except Exception:
            pass

        next_url_params = {k: p[0] for k, p in query_params.copy().items()}
        if 'before' in next_url_params:
            del next_url_params['before']
        next_url_params.update(new_params)
        next_url = build_absolute_uri(
            reverse('post-explore')) + '?' + urllib.parse.urlencode(next_url_params)

        new_params = {}
        if after:
            before_timestamp = after
            new_params['section'] = 1
        elif results.hits.total > (section * item_count):
            before_timestamp = before if before else now
            new_params['section'] = section + 1
        else:
            before_timestamp = None
        if before_timestamp:
            new_params['before'] = str(int(before_timestamp.timestamp() * 1000))
            prev_url_params = {k: p[0] for k, p in query_params.copy().items()}
            if 'after' in prev_url_params:
                del prev_url_params['after']
            prev_url_params.update(new_params)
            prev_url = build_absolute_uri(
                reverse('post-explore')) + '?' + urllib.parse.urlencode(prev_url_params)
        else:
            prev_url = None

        return Response(
            {
                "status": "success",
                "error": "",
                "count": results.hits.total,
                # in haystack view next will go backwards. Deprecated. New clients should
                # use forward and backward.
                "next": prev_url,
                # in haystack view previous will go forwards. Deprecated. New clients should
                # use forward and backward.
                "previous": next_url,
                "forward": next_url,
                "backward": prev_url,
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def update_interest_relevance(self, interest_name, user):
        try:
            interest = Interest.objects.get(name=interest_name)
        except Interest.DoesNotExist:
            return

        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            relevance = UserInterestRelevance.objects.get(interest=interest, user=user)
        except UserInterestRelevance.DoesNotExist:
            relevance = UserInterestRelevance.objects.create(
                interest=interest,
                user=user,
                last_reset=now,
                weekly_views=0,
                old_views=0,
            )

        if relevance.last_reset < (now - datetime.timedelta(weeks=1)):
            decay = 0.5
            relevance.last_reset = now
            relevance.old_views = int(relevance.old_views * decay) + relevance.weekly_views
            relevance.weekly_views = 0

        relevance.weekly_views += 1

        relevance.save()


class PostHSerializer(HaystackSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        index_classes = [PostIndex]
        fields = [
            "text",
        ]


class PostSearchView(HaystackViewSet):
    index_models = [Post]
    serializer_class = PostSearchSerializer

    def filter_queryset(self, *args, **kwargs):
        queryset = super(PostSearchView, self).filter_queryset(
            self.get_queryset())
        return queryset.order_by('-created_on')


class UserTopicParamSerializer(serializers.Serializer):
    is_work = serializers.NullBooleanField(default=None)

class UserTopicsListView(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, user_id):
        serializer = UserTopicParamSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'status': 'failed', 'error':serializer.errors, 'results':None},
                            status.HTTP_400_BAD_REQUEST)
        is_work = serializer.data['is_work']

        user_topics = UserTopic.objects.filter(user_id=user_id).order_by('-popularity', 'topic')
        if is_work is not None:
            user_topics = user_topics.filter(is_work=is_work)
        else:
            user_topics = user_topics.filter(is_work__isnull=True)

        serializer = UserTopicSerializer(user_topics, many=True)

        return Response({
            'status': 'success',
            'error': None,
            'results': {
                'user_topics': serializer.data
            }
        })
