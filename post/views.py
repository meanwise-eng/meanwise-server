import json
import datetime
import urllib
import arrow
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F, When, Case, IntegerField, Count, Subquery, OuterRef, Value
from django.db.models.functions import Coalesce
from django.utils.datastructures import MultiValueDictKeyError
from django.db import transaction
from django.core.exceptions import PermissionDenied
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

from post.models import *
from post.serializers import *
from userprofile.models import UserFriend, Interest
from mnotifications.models import Notification

from elasticsearch_dsl import query
from post.search_indexes import PostIndex
from common.api_helper import get_objects_paginated
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
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrReadOnly,)

    def get(self, request, user_id):
        posts = post_qs.filter(poster__id=user_id)
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        posts, has_next_page, num_pages = get_objects_paginated(
            posts, page, page_size)
        serializer = PostSerializer(
            posts, many=True, context={'request': request})
        return Response({"status": "success", "error": "", "results": {"data": serializer.data, "num_pages": num_pages}}, status=status.HTTP_200_OK)

    @transaction.atomic()
    def post(self, request, user_id):
        data = request.data.copy()
        data['poster'] = user_id

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
            post = serializer.save()
            if topic_names:
                topic_names = topic_names.split(",")
                for topic in topic_names:
                    try:
                        t = Topic.objects.get(text=topic)
                    except Topic.DoesNotExist:
                        t = Topic.objects.create(text=topic)
                    post.topics.add(t)

            mentioned_users = serializer.validated_data.get('mentioned_users')
            if len(mentioned_users):
                for i in range(len(mentioned_users)):
                    try:
                        m = User.objects.get(pk=mentioned_users[i].id)
                    except User.DoesNotExist:
                        pass
                    post.mentioned_users.add(m)

                    # Add notification
                    notification = Notification.objects.create(
                        receiver=m,
                        notification_type=Notification.TYPE_UNKNOWN,
                        data={
                            'post_mentioned_user': m.id,
                            'mentioned_by': int(user_id),
                            'post_id': post.id
                        },
                        post=post)
                    # send push notification
                    devices = find_user_devices(mentioned_users[i].id)
                    message_payload = {'p': str(post.id), 'u': str(mentioned_users[i].id), 't': 'l', 'message': (str(
                        user.userprofile.first_name) + " " + str(user.userprofile.last_name) + "has mentioned you in a post")}
                    for device in devices:
                        send_message_device(device, message_payload)

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

            return Response({"status": "success", "error": "", "results": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "failed", "error": serializer.errors, "results": ""}, status=status.HTTP_400_BAD_REQUEST)


class UserPostDetail(APIView):
    """
    Delete a post instance.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrReadOnly,)

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
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
        return Response({"status": "success", "error": "", "results": "Succesfully deleted."}, status=status.HTTP_202_ACCEPTED)


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
            return Response({"status": "success", "error": "", "results": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "failed", "error": str(e), "results": ""}, status=status.HTTP_400_BAD_REQUEST)


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
                return Response({"status": "failed", "error": "Error fetching userprofile/interests for user.", "results": ""}, status=status.HTTP_400_BAD_REQUEST)
            interests_ids = userprofile.interests.all().values_list('id', flat=True)
            posts = post_qs.filter(interest__id__in=interests_ids)
            serializer = PostSerializer(
                posts, many=True, context={'request': request})
            return Response({"status": "success", "error": "", "results": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "failed", "error": str(e), "results": ""}, status=status.HTTP_400_BAD_REQUEST)


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
        return Response({"status": "success", "error": "", "results": serializer.data}, status=status.HTTP_200_OK)


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
                return Response({"status": "failed", "error": "Error fetching userprofile/interests for user.", "results": ""}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response({"status": "success", "error": "", "results": {"data": serializer.data, "num_pages": num_pages}}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(e)

            return Response({"status": "failed", "error": str(e), "results": ""}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"status": "failed", "error": str(e), "results": ""}, status=status.HTTP_400_BAD_REQUEST)


class PublicFeed(APIView):

    def get(self, request):
        posts = post_qs.all()[:20]
        serializer = PostSerializer(
            posts, many=True, context={'request': request})
        return Response({"status": "success", "error": "", "results": {"data": serializer.data}}, status=status.HTTP_200_OK)


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

        post.liked_by.add(user)
        # Add notification
        notification = Notification.objects.create(
            receiver=post.poster,
            notification_type=Notification.TYPE_LIKED_POST,
            post=post, post_liked_by=user)
        # send push notification
        devices = find_user_devices(post.poster.id)
        message_payload = {'p': str(post.id), 'u': str(post.poster.id), 't': 'l', 'message': (str(
            user.userprofile.first_name) + " " + str(user.userprofile.last_name) + " liked your post")}
        for device in devices:
            send_message_device(device, message_payload)
        return Response({"status": "success", "error": "", "results": "Succesfully liked."}, status=status.HTTP_202_ACCEPTED)


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
            return Response({"status": "success", "error": "", "results": "Succesfully unliked."}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"status": "failed", "error": "User not in liked list", "results": ""}, status=status.HTTP_202_ACCEPTED)


class PostLikes(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_post(self, post_id):
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, post_id):
        post = self.get_post(post_id)

        page = request.GET.get('page')
        page_size = request.GET.get('page_size')

        liked_by_query = UserProfile.objects.filter(
            user__in=post.liked_by.all()).order_by('username').all()
        liked_by, has_next_page, num_pages = get_objects_paginated(
            liked_by_query, page, page_size)

        serializer = UserProfileSerializer(
            liked_by, many=True, context={'request': request})
        return Response({"status": "success", "error": "", "results": {"data": serializer.data, "num_pages": num_pages}}, status=status.HTTP_200_OK)


class PostLikes(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_post(self, post_id):
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, post_id):
        post = self.get_post(post_id)

        page = request.GET.get('page')
        page_size = request.GET.get('page_size')

        liked_by_query = UserProfile.objects.filter(
            user__in=post.liked_by.all()).order_by('username').all()
        liked_by, has_next_page, num_pages = get_objects_paginated(
            liked_by_query, page, page_size)

        serializer = UserProfileSerializer(
            liked_by, many=True, context={'request': request})
        return Response({"status": "success", "error": "", "results": {"data": serializer.data, "num_pages": num_pages}}, status=status.HTTP_200_OK)


class PostCommentList(APIView):
    """
    List all post related comments, or create a new User comment.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, post_id):
        comments = Comment.objects.filter(is_deleted=False).filter(
            post__id=post_id).order_by('-created_on')
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        comments, has_next_page, num_pages = get_objects_paginated(
            comments, page, page_size)
        serializer = CommentSerializer(comments, many=True)
        return Response({"status": "success", "error": "", "results": {"data": serializer.data, "num_pages": num_pages}}, status=status.HTTP_200_OK)

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
                logger.info("Comment saved")
                # Add notification
                notification = Notification.objects.create(
                    receiver=comment.post.poster,
                    notification_type=Notification.TYPE_COMMENTED_POST,
                    post=comment.post,
                    comment=comment)
                # send push notification
                devices = find_user_devices(comment.post.poster.id)
                message_payload = {'p': str(comment.post.id), 'u': str(comment.post.poster.id),
                                   't': 'c', 'message': (str(comment.commented_by.userprofile.first_name) + " " + str(comment.commented_by.userprofile.last_name) + " commented on your post")}

                logger.info("No of devices to send: %s" % len(devices))
                for device in devices:
                    logger.info("Sending notification to device: %s" % device)
                    send_message_device(device, message_payload)

                mentioned_users = serializer.validated_data.get(
                    'mentioned_users')

                if len(mentioned_users):
                    for i in range(len(mentioned_users)):
                        try:
                            m = User.objects.get(pk=mentioned_users[i].id)
                        except User.DoesNotExist:
                            pass
                        comment.mentioned_users.add(m)

                        # Add notification
                        notification = Notification.objects.create(
                            receiver=m,
                            notification_type=Notification.TYPE_UNKNOWN,
                            comment=comment,
                            data={
                                'comment_mentioned_user': m.id,
                                'mentioned_by': comment.commented_by.id,
                                'comment_id': comment.id
                            })
                        # send push notification
                        devices = find_user_devices(mentioned_users[i].id)
                        message_payload = {
                            'p': str(comment.id),
                            'u': str(comment.commented_by.id),
                            't': 'l',
                            'message': (str(comment.commented_by.userprofile.first_name) + " " + str(comment.commented_by.userprofile.last_name) + "has mentioned you in a comment")
                        }
                        for device in devices:
                            send_message_device(device, message_payload)

                return Response({"status": "success", "error": "", "results": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as ex:
                logger.error(ex)
                return Response({"status": "failed", "error": "Error saving comment.", "results": ""}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"status": "failed", "error": serializer.errors, "results": ""}, status=status.HTTP_400_BAD_REQUEST)


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
              'comment_text', 'created_on', 'modified_on')


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

        return Response({"status": "success", "error": "", "results": tags}, status=status.HTTP_201_CREATED)


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

        return Response({"status": "success", "error": "", "results": topics}, status=status.HTTP_201_CREATED)


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
            return Response({"status": "failed", "error": "Interest with given id does not Exist", "results": ""}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tt = TrendingTopicsInterest.objects.get(interest=interest)
        except TrendingTopicsInterest.DoesNotExist:
            return Response({"status": "failed", "error": "Could not find relevant value in TrendingTopicsInterest.", "results": ""}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "success", "error": "", "results": tt.topics}, status=status.HTTP_201_CREATED)

class PostExploreView(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        interest_name = request.query_params.get('interest_name', None)
        topic_texts = request.query_params.get('topic_texts', None)
        tag_names = request.query_params.get('tag_names', None)
        after = request.query_params.get('after', None)
        before = request.query_params.get('before', None)
        if after:
            after = datetime.datetime.fromtimestamp(float(after)/1000)
        if before:
            before = datetime.datetime.fromtimestamp(float(before)/1000)

        items_per_page = 30

        interest_ids = list(request.user.userprofile.interests.all().values_list('id', flat=True))
        friends_ids = list(UserFriend.objects.filter(Q(user_id=request.user.id)).all().values_list('id', flat=True)) + \
            list(UserFriend.objects.filter(Q(friend_id=request.user.id)).all().values_list('id', flat=True))
        skills_list = request.user.userprofile.skills_list

        functions = []
        filters = []
        must = []
        if interest_name:
            must.append(query.Q('term', interest_name=interest_name))
            #functions.append(query.SF({'filter':query.Q('term', interest_name=interest_name), 'weight': 1}))
        if topic_texts:
            must.append(query.Q('match', topics=topic_texts))
            #functions.append(query.SF({'filter':query.Q('match', topics=topic_texts), 'weight': 3}))
        if tag_names:
            must.append(query.Q('match', tags=tag_names))
            #functions.append(query.SF({'filter':query.Q('match', tags=tag_names), 'weight': 3}))
        if after:
            filters.append(query.Q({'range': {'created_on':{'gt': after}}}))
        if before:
            filters.append(query.Q({'range': {'created_on':{'lt': before}}}))


        now = datetime.datetime.now()

        # overall popularity
        functions.append(query.SF('exp', created_on={'origin': now, 'offset': '1m', 'scale': '5m', 'decay': 0.9}, weight=5))
        functions.append(query.SF('exp', created_on={'origin': now, 'offset': '1d', 'scale': '1d', 'decay': 0.9}, weight=4))
        functions.append(query.SF('field_value_factor', field='num_likes', modifier='log1p', weight=2))
        functions.append(query.SF('field_value_factor', field='num_comments', modifier='log1p', weight=3))
        functions.append(query.SF('field_value_factor', field='num_seen', modifier='log1p', weight=1))

        # relevance to user
        functions.append(query.SF({'filter': query.Q('terms', user_id=friends_ids), 'weight': 1}))
        functions.append(query.SF({'filter': query.Q('terms', interest_id=interest_ids), 'weight': 1}))
        functions.append(query.SF({'filter': query.Q('match', tags=" ".join(skills_list)), 'weight': 1}))

        s = PostDocument.search()
        if len(filters) > 0:
            q = query.Q(
                'function_score',
                query=query.Q('bool', must=must, filter=filters),
                functions=functions,
                score_mode='sum'
            )
        else:
            q = query.Q(
                'function_score',
                functions=functions,
                score_mode='sum'
            )
        s = s.query(q)
        s = s[0:items_per_page]

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

        if after and results.hits.total > 30:
            max_created_on = reduce(get_biggest_date, [result.created_on for result in results])
        elif before and results.hits.total == 0:
            max_created_on = before
        else:
            max_created_on = now
        next_url_params = query_params.copy()
        if 'before' in next_url_params: del next_url_params['before']
        next_url_params.update({'after': str(int(max_created_on.timestamp()*1000))})
        next_url = request.build_absolute_uri(reverse('post-explore')) + '?' + urllib.parse.urlencode(next_url_params)

        if results.hits.total != 0:
            min_created_on = reduce(get_smallest_date, [result.created_on for result in results])
        elif not before:
            min_created_on = now
        else:
            min_created_on = None

        if min_created_on:
            prev_url_params = query_params.copy()
            if 'after' in prev_url_params: del prev_url_params['after']
            prev_url_params.update({'before': str(int(min_created_on.timestamp()*1000))})
            prev_url = request.build_absolute_uri(reverse('post-explore')) + '?' + urllib.parse.urlencode(prev_url_params)
        else:
            prev_url = None

        return Response(
            {
                "status": "success",
                "error": "",
                "count": results.hits.total,
                "next": prev_url,  # in haystack view next will go backwards. Deprecated. New clients should use forward and backward.
                "previous": next_url,  # in haystack view next will go forwards. Deprecated. New clients should use forward and backward.
                "forward": next_url,
                "backward": prev_url,
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )

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
