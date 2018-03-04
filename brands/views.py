import datetime
import logging

from django.conf import settings
from django.http import Http404
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from common.api_helper import build_absolute_uri, TimeBasedPaginator

from elasticsearch_dsl import query

from django.contrib.contenttypes.models import ContentType
from follow.models import Follow

from userprofile.models import UserFriend, UserProfile
from userprofile.serializers import UserProfileSerializer
from post.serializers import PostSerializer

from .models import Brand
from .documents import BrandDocument
from .serializers import BrandSerializer, BrandDocumentSerializer, OrgDocumentSummarySerializer

from post.documents import ExploreOrgDocument

logger = logging.getLogger('meanwise_backend.%s' % __name__)


class BrandListView(APIView):

    def get(self, request):
        interest_id = request.query_params.get('interest_id', None)
        tag_name = request.query_params.get('tag_name', None)
        topic_text = request.query_params.get('topic_text', None)
        item_count = request.query_params.get('item_count', settings.REST_FRAMEWORK['PAGE_SIZE'])
        section = request.query_params.get('section', 1)
        before = request.query_params.get('before', None)
        if before:
            before = datetime.datetime.fromtimestamp(float(before) / 1000)

        interest_ids = list(request.user.userprofile.interests.all().values_list('id', flat=True))
        friends_ids = list(UserFriend.objects.filter(Q(user_id=request.user.id)).all().values_list('friend_id', flat=True)) + \
            list(UserFriend.objects.filter(Q(friend_id=request.user.id)).all().values_list('user_id', flat=True))
        skills_list = request.user.userprofile.skills_list

        functions = []
        filters = []
        must = []
        if interest_id:
            must.append(query.Q('term', interest_ids=interest_id))
        # else:
        #     filters.append(query.Q('bool', should=[
        #         query.Q('terms', interest_ids=interest_ids),
        #         query.Q('terms', user_id=friends_ids)
        #     ]))
        if topic_text:
            must.append(query.Q('match', topics=topic_text))
        if tag_name:
            must.append(query.Q('match', tags=tag_name))

        now = datetime.datetime.now()
        origin = before if before else now

        must.append(query.Q({'range': {'created_on': {'lt': origin}}}))

        # manual boost
        functions.append(query.SF('exp', boost_datetime={
            'origin': origin, 'scale': '1d', 'decay': 0.1},
            weight=5))
        functions.append(query.SF('field_value_factor', field='boost_value',
                                  modifier='log1p', weight=30, missing=0))

        s = BrandDocument.search()
        q = query.Q(
            'function_score',
            query=query.Q('bool', must=must, filter=filters),
            functions=functions,
            score_mode='sum',
            boost_mode='sum'
        )
        s = s.query(q)
        logger.info(s.to_dict())
        offset = (section - 1) * item_count
        s = s[offset:offset + item_count]

        results = s.execute()
        serializer = BrandDocumentSerializer(results, many=True, context={'request': request})

        total = results.hits.total

        back_url = None
        if total > section * item_count:
            params = {'before': str(int(origin.timestamp() * 1000)), 'section': section + 1}
            back_url = build_absolute_uri(request.get_full_path(), params=params)

        return Response({
            'status': 'success',
            'error': None,
            'results': serializer.data,
            'forward': None,
            'backward': back_url,
            'total': total
        }, status.HTTP_200_OK)


class OrgListView(APIView):

    def get(self, request):
        interest_id = request.query_params.get('interest_id', None)
        tag_name = request.query_params.get('tag_name', None)
        topic_text = request.query_params.get('topic_text', None)
        item_count = request.query_params.get('item_count', settings.REST_FRAMEWORK['PAGE_SIZE'])
        section = request.query_params.get('section', 1)
        before = request.query_params.get('before', None)
        if before:
            before = datetime.datetime.fromtimestamp(float(before) / 1000)

        interest_ids = list(request.user.userprofile.interests.all().values_list('id', flat=True))
        friends_ids = list(UserFriend.objects.filter(Q(user_id=request.user.id)).all().values_list('friend_id', flat=True)) + \
            list(UserFriend.objects.filter(Q(friend_id=request.user.id)).all().values_list('user_id', flat=True))
        skills_list = request.user.userprofile.skills_list

        functions = []
        filters = []
        must = []
        #if interest_id:
        #    must.append(query.Q('term', interest_ids=interest_id))
        # else:
        #     filters.append(query.Q('bool', should=[
        #         query.Q('terms', interest_ids=interest_ids),
        #         query.Q('terms', user_id=friends_ids)
        #     ]))
        #if topic_text:
        #    must.append(query.Q('match', topics=topic_text))
        #if tag_name:
        #    must.append(query.Q('match', tags=tag_name))

        now = datetime.datetime.now()
        origin = before if before else now

        must.append(query.Q({'range': {'created_on': {'lt': origin}}}))

        # manual boost
        #functions.append(query.SF('exp', boost_datetime={
        #    'origin': origin, 'scale': '1d', 'decay': 0.1},
        #    weight=5))
        #functions.append(query.SF('field_value_factor', field='boost_value',
        #                          modifier='log1p', weight=30, missing=0))

        s = ExploreOrgDocument.search()
        q = query.Q(
            'function_score',
            query=query.Q('bool', must=must, filter=filters),
            functions=functions,
            score_mode='sum',
            boost_mode='sum'
        )
        s = s.query(q)
        logger.info(s.to_dict())
        offset = (section - 1) * item_count
        s = s[offset:offset + item_count]

        results = s.execute()
        serializer = OrgDocumentSummarySerializer(results, many=True, context={'request': request})

        total = results.hits.total

        back_url = None
        if total > section * item_count:
            params = {'before': str(int(origin.timestamp() * 1000)), 'section': section + 1}
            back_url = build_absolute_uri(request.get_full_path(), params=params)

        return Response({
            'status': 'success',
            'error': None,
            'results': serializer.data,
            'forward': None,
            'backward': back_url,
            'total': total
        }, status.HTTP_200_OK)


class BrandDetailsView(APIView):

    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.AllowAny, )

    def get(self, request, brand_id):
        try:
            brand = Brand.objects.get(pk=brand_id)
        except Brand.DoesNotExist:
            raise Http404

        serializer = BrandSerializer(brand)

        return Response({
            'status': 'success',
            'error': None,
            'results': serializer.data
        }, status.HTTP_200_OK)


class BrandMembersView(APIView):

    def get(self, request, brand_id):
        try:
            brand = Brand.objects.get(pk=brand_id)
        except Brand.DoesNotExist:
            return Http404

        userprofiles = UserProfile.objects.filter(user__brandmember__brand=brand)
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


class BrandPostsView(APIView):

    def get(self, request, brand_id):
        try:
            brand = Brand.objects.get(pk=brand_id)
        except Brand.DoesNotExist:
            return Http404

        posts = brand.posts.all()
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


class FollowBrandView(APIView):

    def post(self, request, brand_id):
        try:
            brand = Brand.objects.get(pk=brand_id)
        except Brand.DoesNotExist:
            return Http404

        follow = Follow(follower_object=request.user, followee_object=brand)
        follow.save()

        return Response({
            'status': 'success',
            'error': None,
            'results': {'message': 'Succesfully followed'}
        }, status.HTTP_200_OK)


class UnfollowBrandView(APIView):

    def post(self, request, brand_id):
        try:
            brand = Brand.objects.get(pk=brand_id)
        except Brand.DoesNotExist:
            return Http404

        user_content_type = ContentType.objects.get_for_model(request.user.__class__)
        brand_content_type = ContentType.objects.get_for_model(Brand)
        follow = Follow.objects.filter(
            follower_id=request.user.id, follower_content_type=user_content_type,
            followee_id=brand.id, followee_content_type=brand_content_type)
        follow.delete()

        return Response({
            'status': 'success',
            'error': None,
            'results': {'message': 'Succesfully unfollowed'}
        }, status.HTTP_200_OK)
