import urllib
import datetime
import operator
from functools import reduce

from rest_framework import authentication, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from common.api_helper import build_absolute_uri

from django.urls import reverse
from django.db.models import Q

from .serializers import DiscussionItemSerializer
from .models import DiscussionItem


class DiscussionListView(APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        interest_name = request.query_params.get('interest_name', None)
        topic_texts = request.query_params.get('topic_texts', None)
        tag_names = request.query_params.get('tag_names', None)
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

        discussions = DiscussionItem.objects.order_by('-datetime')

        if interest_name:
            discussions = discussions.filter(post__interest__name__iexact=interest_name)
        elif user_id is None:
            interest_names = list(request.user.userprofile.interests.all()
                                  .values_list('name', flat=True))

            filters = []
            for interest_name in interest_names:
                filters.append(Q(post__interest__name__iexact=interest_name))
            discussions = discussions.filter(reduce(operator.or_, filters))

        if topic_texts:
            discussions = discussions.filter(post__topic__text__iexact=topic_texts)

        if tag_names:
            discussions = discussions.filter(post__tags__name__iexact=tag_names)

        if user_id:
            discussions = discussions.filter(user=user_id)

        now = datetime.datetime.now()

        if after:
            discussions = discussions.filter(datetime__gte=after)
        if before:
            discussions = discussions.filter(datetime__lte=before)

        total = discussions.count()

        query_params = dict(request.query_params)

        after_date = before if before else now

        new_params = {}
        try:
            new_params['after'] = str(int(after_date.timestamp() * 1000))
        except Exception:
            pass
        next_url_params = {k: p[0] for k, p in query_params.copy().items()}
        if 'before' in next_url_params:
            del next_url_params['before']
        next_url_params.update(new_params)
        next_url = build_absolute_uri(
            reverse('discussions-list')) + '?' + urllib.parse.urlencode(next_url_params)

        new_params = {}
        if before:
            before_date = before
            new_params['section'] = section + 1
        else:
            before_date = now
            new_params['section'] = 2

        if before_date and section * item_count < total:
            try:
                new_params['before'] = str(int(before_date.timestamp() * 1000))
            except Exception:
                pass

            prev_url_params = {k: p[0] for k, p in query_params.copy().items()}
            if 'after' in prev_url_params:
                del prev_url_params['after']
            prev_url_params.update(new_params)
            prev_url = build_absolute_uri(
                reverse('discussions-list')) + '?' + urllib.parse.urlencode(prev_url_params)
        else:
            prev_url = None

        offset = (section - 1) * item_count
        serializer = DiscussionItemSerializer(
            discussions[offset:offset + item_count],
            many=True,
            context={'request': request}
        )

        return Response(
            {
                "status": "success",
                "error": None,
                "count": total,
                "forward": next_url,
                "backward": prev_url,
                "results": serializer.data
            },
            status=status.HTTP_200_OK)
