from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet

from post.models import Post, Comment, Share
from post.serializers import PostSerializer, CommentSerializer, ShareSerializer

from post.search_indexes import PostIndex

class PostViewSet(viewsets.ModelViewSet):
    """
    Post apis

    """
    queryset = Post.objects.all()
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


        
class CommentViewSet(viewsets.ModelViewSet):
    """
    Comment apis

    """
    queryset = Comment.objects.all()
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



class PostSerializer(HaystackSerializer):
    class Meta:
        index_classes = [PostIndex]
        fields = [
            "text", "post_text"
        ]

class PostSearchView(HaystackViewSet):
    index_models = [Post]
    serializer_class = PostSerializer