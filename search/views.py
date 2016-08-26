from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from haystack.generic_views import SearchView
from haystack.inputs import AutoQuery, Clean
from haystack.query import SearchQuerySet, SQ

from common.constants import UNAUTHENTICATED_NOT_LOGGEDIN
from account_profile.models import Profile
from jobs.models import Job
from jobs.serializers import JobSerializer

from .serializers import SearchProfileSerializer
from .pagination import SearchPagination

sqs = SearchQuerySet()


@api_view(http_method_names=['GET'])
def search_view(request):
    q = request.GET.get('q', '')
    queryset = SearchQuerySet().filter(content_auto=q).models(Profile)
    paginator = SearchPagination()
    result_page = paginator.paginate_queryset(queryset, request)
    profile_ids = []
    for result in result_page:
        if result:
            profile_ids.append(result.pk)
    profiles = Profile.objects.filter(pk__in=profile_ids)
    serializer = SearchProfileSerializer(profiles, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
def search_jobs(request):
    """
        Grabs a list of recommended jobs based on user_query
        Assume user_query is space separated. Searches each by each word.
        Ex. search - 'Python Java Django'

        Ex. Request
        {
            user_query: 'Python Django'
        }
    """
    if request.method == 'POST':
        user_query = request.data['user_query']
        jobs = sqs.models(Job)
        clean_query = sqs.query.clean(user_query)
        jobResults = jobs.filter(SQ(text=clean_query) |
                                 SQ(skills__in=clean_query.lower().split(' ')))
        if jobResults.count() == 0:
            return Response('Failed to find any jobs with this query.')
        instances = [job.object for job in jobResults]
        serializer = JobSerializer(instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
