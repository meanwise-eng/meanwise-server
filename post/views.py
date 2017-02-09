from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.http import Http404
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import authentication, permissions

from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet

from post.models import Post, Comment, Share
from post.serializers import *
from userprofile.models import UserFriend

from post.search_indexes import PostIndex

class UserPostList(APIView):
    """
    List all User posts, or create a new User post.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        posts = Post.objects.filter(is_deleted=False).filter(poster__id=user_id).order_by('-created_on')
        serializer = PostSerializer(posts, many=True)
        return Response({"status":"success", "error":"", "results":serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        data = request.data
        request.data['poster'] = user_id
        serializer = PostSaveSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
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
        serializer = CommentSerializer(comments, many=True)
        return Response({"status":"success", "error":"", "results":serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        data = request.data
        data['post'] = post_id
        serializer = CommentSaveSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
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
    queryset = Comment.objects.all().order_by('-created_on')
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



class PostHSerializer(HaystackSerializer):
    class Meta:
        index_classes = [PostIndex]
        fields = [
            "text", "post_text", "id", "interest_name"
        ]

class PostSearchView(HaystackViewSet):
    index_models = [Post]
    serializer_class = PostHSerializer