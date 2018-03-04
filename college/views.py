from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from common.api_helper import build_absolute_uri, TimeBasedPaginator
from django.http import Http404

from django.contrib.contenttypes.models import ContentType
from follow.models import Follow

from userprofile.models import UserProfile
from userprofile.serializers import UserProfileSerializer
from post.models import Post
from post.serializers import PostSerializer
from .models import College
from .serializers import CollegeSerializer

class CollegeDetailsView(APIView):

    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.AllowAny, )

    def get(self, request, college_id):
        try:
            college = College.objects.get(pk=college_id)
        except College.DoesNotExist:
            raise Http404

        serializer = CollegeSerializer(college)

        return Response({
            'status': 'success',
            'error': None,
            'results': serializer.data
        }, status.HTTP_200_OK)


class CollegeStudentsView(APIView):

    def get(self, request, college_id):
        try:
            college = College.objects.get(pk=college_id)
        except College.DoesNotExist:
            return Http404

        userprofiles = UserProfile.objects.filter(user__featuredstudent__college=college)
        paginator = TimeBasedPaginator(userprofiles, request)
        serializer = UserProfileSerializer(paginator.page(), many=True, context={'request': request})

        return Response({
            'status': 'success',
            'error': None,
            'results': serializer.data,
            'total': paginator.total,
            'forward': paginator.next_url,
            'backward': paginator.prev_url
        }, status.HTTP_200_OK)


class CollegePostsView(APIView):

    def get(self, request, college_id):
        try:
            college = College.objects.get(pk=college_id)
        except College.DoesNotExist:
            return Http404

        posts = college.posts.all()
        paginator = TimeBasedPaginator(posts, request)
        serializer = PostSerializer(paginator.page(), many=True, context={'request': request})

        return Response({
            'status': 'success',
            'error': None,
            'results': serializer.data,
            'total': paginator.total,
            'forward': paginator.next_url,
            'backward': paginator.prev_url
        }, status.HTTP_200_OK)


class FollowCollegeView(APIView):

    def post(self, request, college_id):
        try:
            college = College.objects.get(pk=college_id)
        except College.DoesNotExist:
            return Http404

        follow = Follow(follower_object=request.user, followee_object=college)
        follow.save()

        return Response({
            'status': 'success',
            'error': None,
            'results': {'message': 'Succesfully followed'}
        }, status.HTTP_200_OK)


class UnfollowCollegeView(APIView):

    def post(self, request, college_id):
        try:
            college = College.objects.get(pk=college_id)
        except College.DoesNotExist:
            return Http404

        user_content_type = ContentType.objects.get_for_model(request.user.__class__)
        brand_content_type = ContentType.objects.get_for_model(College)
        follow = Follow.objects.filter(
            follower_id=request.user.id, follower_content_type=user_content_type,
            followee_id=college.id, followee_content_type=brand_content_type)
        follow.delete()

        return Response({
            'status': 'success',
            'error': None,
            'results': {'message': 'Succesfully unfollowed'}
        }, status.HTTP_200_OK)
