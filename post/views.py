from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.http import Http404
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.datastructures import MultiValueDictKeyError

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

from post.models import *
from post.serializers import *
from userprofile.models import UserFriend, Interest
from mnotifications.models import Notification

from post.search_indexes import PostIndex
from common.api_helper import get_objects_paginated

class UserPostList(APIView):
    """
    List all User posts, or create a new User post.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        posts = Post.objects.filter(is_deleted=False).filter(poster__id=user_id).order_by('-created_on')
        #page = request.GET.get('page')
        #page_size = request.GET.get('page_size')
        #posts, has_next_page, num_pages  = get_objects_paginated(posts, page, page_size)
        serializer = PostSerializer(posts, many=True)
        #return Response({"status":"success", "error":"", "results":{"data":serializer.data, "num_pages":num_pages}}, status=status.HTTP_200_OK)
        return Response({"status":"success", "error":"", "results":serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        data = request.data
        request.data['poster'] = user_id
        serializer = PostSaveSerializer(data=data)
        if serializer.is_valid():
            #handle topics
            topic_names = None
            if serializer.validated_data.get('topic_names', None):
                topic_names = serializer.validated_data.pop('topic_names')
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
            #handle tags
            for t in ts:
                post.tags.add(t)

            return Response({"status":"success", "error":"", "results":serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status":"failed", "error":serializer.errors, "results":""}, status=status.HTTP_400_BAD_REQUEST)

    
class UserPostDetail(APIView):
    """
    Delete a post instance.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404

    def delete(self, request, user_id, post_id):
        post = self.get_object(post_id)
        post.is_deleted= True
        post.save()
        return Response({"status":"success", "error":"", "results":"Succesfully deleted."}, status=status.HTTP_202_ACCEPTED)

class UserFriendsPostList(APIView):
    """
    List all User's friends' posts.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        try:
            friends_ids = UserFriend.objects.filter(user__id=user_id).values_list('friend__id', flat=True)
            posts = Post.objects.filter(is_deleted=False).filter(poster__id__in=friends_ids).order_by('-created_on')
            serializer = PostSerializer(posts, many=True)
            return Response({"status":"success", "error":"", "results":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed", "error":str(e), "results":""}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({"status":"failed", "error":"Error fetching userprofile/interests for user.", "results":""}, status=status.HTTP_400_BAD_REQUEST)
            interests_ids = userprofile.interests.all().values_list('id', flat=True)
            posts = Post.objects.filter(is_deleted=False).filter(interest__id__in=interests_ids).order_by('-created_on')
            serializer = PostSerializer(posts, many=True)
            return Response({"status":"success", "error":"", "results":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed", "error":str(e), "results":""}, status=status.HTTP_400_BAD_REQUEST)
    
class UserHomeFeed(APIView):
    """
    User home feed - comprising 1. User's post 2. User's friend post 3. User's interest based post.

    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        try:
            friends_ids = UserFriend.objects.filter(user__id=user_id).values_list('friend__id', flat=True)
            try:
                userprofile = UserProfile.objects.get(user__id=user_id)
            except UserProfile.DoesNotExist:
                return Response({"status":"failed", "error":"Error fetching userprofile/interests for user.", "results":""}, status=status.HTTP_400_BAD_REQUEST)
            interests_ids = userprofile.interests.all().values_list('id', flat=True)
            home_feed_posts = Post.objects.filter(is_deleted=False).filter(Q(poster__id__in=friends_ids) | Q(interest__id__in=interests_ids) | Q(poster__id=user_id)).order_by('-created_on')
            #page = request.GET.get('page')
            #page_size = request.GET.get('page_size')
            #home_feed_posts, has_next_page, num_pages  = get_objects_paginated(home_feed_posts, page, page_size)
            serializer = PostSerializer(home_feed_posts, many=True)
            #return Response({"status":"success", "error":"", "results":{"data":serializer.data, "num_pages":num_pages}}, status=status.HTTP_200_OK)
            return Response({"status":"success", "error":"", "results":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status":"failed", "error":str(e), "results":""}, status=status.HTTP_400_BAD_REQUEST)

class PostViewSet(viewsets.ModelViewSet):
    """
    Post apis

    """
    queryset = Post.objects.all().order_by('-created_on')
    serializer_class = PostSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'interest', 'image', 'video', 'text', 'poster', 'tags', 'liked_by', 'is_deleted', 'created_on', 'modified_on')
    
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
        post.liked_by.add(user)
        #Add notification
        notification = Notification.objects.create(receiver=post.poster, notification_type='LP',  post=post, post_liked_by=user)
        return Response({"status":"success", "error":"", "results":"Succesfully liked."}, status=status.HTTP_202_ACCEPTED)

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
        if user in post.liked_by.all():
            post.liked_by.remove(user)
            return Response({"status":"success", "error":"", "results":"Succesfully unliked."}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"status":"failed", "error":"User not in liked list", "results":""}, status=status.HTTP_202_ACCEPTED)


class PostCommentList(APIView):
    """
    List all post related comments, or create a new User comment.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, post_id):
        comments = Comment.objects.filter(is_deleted=False).filter(post__id=post_id).order_by('-created_on')
        #page = request.GET.get('page')
        #page_size = request.GET.get('page_size')
        #comments, has_next_page, num_pages  = get_objects_paginated(comments, page, page_size)
        serializer = CommentSerializer(comments, many=True)
        #return Response({"status":"success", "error":"", "results":{"data":serializer.data, "num_pages":num_pages}}, status=status.HTTP_200_OK)
        return Response({"status":"success", "error":"", "results":serializer.data}, status=status.HTTP_200_OK)
    

    def post(self, request, post_id):
        data = request.data
        data['post'] = post_id
        serializer = CommentSaveSerializer(data=data)
        if serializer.is_valid():
            comment = serializer.save()
            #Add notification
            notification = Notification.objects.create(receiver=comment.post.poster, notification_type='CP',  post=comment.post, comment=comment)
            return Response({"status":"success", "error":"", "results":serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status":"failed", "error":serializer.errors, "results":""}, status=status.HTTP_400_BAD_REQUEST)

    
class PostCommentDetail(APIView):
    """
    Delete a comment instance.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404

    def delete(self, request, post_id, comment_id):
        comment = self.get_object(comment_id)
        comment.is_deleted= True
        comment.save()
        return Response({"status":"success", "error":"", "results":"Succesfully deleted."}, status=status.HTTP_202_ACCEPTED)
        
class CommentViewSet(viewsets.ModelViewSet):
    """
    Comment apis

    """
    queryset = Comment.objects.all().order_by('-created_on').filter(is_deleted=False)
    serializer_class = CommentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'post', 'commented_by', 'comment_text', 'created_on', 'modified_on')

class ShareViewSet(viewsets.ModelViewSet):
    """
    Share apis

    """
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'post', 'messag', 'shared_by', 'recepients', 'created_on', 'modified_on')

class AutocompleteTag(APIView):
    """
    Auto complete tags for given text
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        tag_text = request.data.get('tag', '')
        try:
            tags = Tag.objects.filter(name__istartswith=tag_text).values_list('name', flat=True)
        except MultiValueDictKeyError:
            pass

        return Response({"status":"success", "error":"", "results":tags}, status=status.HTTP_201_CREATED)

class AutocompleteTopic(APIView):
    """
    Auto complete topics for given text
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        topic_text = request.data.get('topic', '')
        try:
            topics = Topic.objects.filter(text__istartswith=topic_text).values_list('text', flat=True)
        except MultiValueDictKeyError:
            pass

        return Response({"status":"success", "error":"", "results":topics}, status=status.HTTP_201_CREATED)

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
            return Response({"status":"failed", "error":"Interest with given id does not Exist", "results":""}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tt = TrendingTopicsInterest.objects.get(interest=interest)
        except TrendingTopicsInterest.DoesNotExist:
            return Response({"status":"failed", "error":"Could not find relevant value in TrendingTopicsInterest.", "results":""}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status":"success", "error":"", "results":tt.topics}, status=status.HTTP_201_CREATED)
    
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
        queryset = super(PostSearchView, self).filter_queryset(self.get_queryset())
        return queryset.order_by('-created_on')