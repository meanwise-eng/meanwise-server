from django.db.models import ObjectDoesNotExist

from rest_framework import viewsets
from rest_framework.response import Response
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

from account_profile.models import Profile
from common.models import Comment
from common.http import JsonErrorResponse
from common.serializers import CommentSerializer
from common.constants import (UNAUTHENTICATED_NOT_LOGGEDIN,
                              GENERIC_ERROR_RESPONSE,
                              GENERIC_NOT_FOUND, UNAUTHORIZED)

from .models import Work, Workitem
from .constants import WorkState, WORK_NOT_FOUND, WORKITEM_NOT_FOUND
from .serializers import WorkSerializer, WorkitemSerializer


class WorkAPIViewSet(viewsets.ModelViewSet):
    model = Work

    def get_queryset(self, profile):
        return Work.objects.live().filter(profile=profile)

    def retrieve(self, request, pk):
        try:
            work = Work.objects.live().get(pk=pk)
        except ObjectDoesNotExist as e:
            return JsonErrorResponse(WORK_NOT_FOUND, status=404)

        if request.user.is_authenticated():
            profile = request.user.profile
        else:
            profile = None

        if work.state == WorkState.PUBLISHED or profile == work.profile:
            hit_count = HitCount.objects.get_for_object(work)
            hit_count_response = HitCountMixin.hit_count(request, hit_count)
            work = WorkSerializer(work, context={'profile': profile}).data
            return Response({'work': work})
        else:
            return JsonErrorResponse(WORK_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        try:
            profile = Profile.objects.get_by_username_id(username)
        except ObjectDoesNotExist as e:
            return Response({'work': []})
        if request.user.is_authenticated():
            loggedIn = request.user.profile
        else:
            loggedIn = None
        if loggedIn == profile:
            works = Work.objects.live().filter(profile=profile)
        else:
            works = Work.objects.live().filter(profile=profile,
                                               state=WorkState.PUBLISHED)
        works = WorkSerializer(works, context={'profile': loggedIn},
                               many=True).data
        return Response({'work': works})

    def create(self, request):
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        data = request.data.get('work', {})
        profile = request.user.profile
        serializer = WorkSerializer(data=data, partial=True)
        if serializer.is_valid():
            work = serializer.create_or_update(serializer.validated_data,
                                               profile)
            work_data = WorkSerializer(work, context={'profile': profile}).data
            return Response({'work': work_data})
        else:
            print (serializer.errors)
            return JsonErrorResponse(serializer.errors)

    def partial_update(self, request, pk):
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        data = request.data.get('work', {})
        profile = request.user.profile
        serializer = WorkSerializer(data=data)
        try:
            work = self.get_queryset(profile).get(pk=pk)
        except ObjectDoesNotExist as e:
            return JsonErrorResponse(WORK_NOT_FOUND, status=404)
        if serializer.is_valid():
            work = serializer.create_or_update(serializer.validated_data,
                                               profile, work)
            work_data = WorkSerializer(work, context={'profile': profile}).data
            return Response({'work': work_data})
        else:
            print (serializer.errors)
            return JsonErrorResponse(serializer.errors)

    def update(self, request, pk):
        raise Exception('Not Implemented')

    def destroy(self, request, pk):
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        profile = request.user.profile
        try:
            work = self.get_queryset(profile).get(pk=pk)
        except ObjectDoesNotExist as e:
            return JsonErrorResponse(WORK_NOT_FOUND, status=404)
        work.delete()
        return Response(status=204)


class WorkitemAPIViewSet(viewsets.ModelViewSet):
    model = Workitem

    def get_queryset(self, work):
        return Workitem.objects.filter(work=work)

    def create(self, request, work_pk, *args, **kwargs):
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        data = request.data.get('workitem', {})
        profile = request.user.profile
        work = Work.objects.live().get(pk=work_pk, profile=profile)
        serializer = WorkitemSerializer(data=data)
        if serializer.is_valid():
            workitem = serializer.create_or_update(serializer.validated_data,
                                                   work)
            workitem_data = WorkitemSerializer(workitem).data
            return Response({'workitem': workitem_data})
        else:
            print (serializer.errors)
            return JsonErrorResponse(serializer.errors)

    def list(self, request, work_pk):
        item_ids = request.query_params.getlist('ids[]')
        try:
            work = Work.objects.live().get(pk=work_pk)
        except ObjectDoesNotExist as e:
            return JsonErrorResponse(WORK_NOT_FOUND, status=404)

        if work.state == WorkState.PUBLISHED or \
                (
                    request.user.is_authenticated()
                    and
                    request.user.profile == work.profile
                ):
            try:
                workitems = Workitem.objects.filter(work_id=work_pk,
                                                    id__in=item_ids)
            except ObjectDoesNotExist as e:
                return JsonErrorResponse(WORKITEM_NOT_FOUND)
            items = WorkitemSerializer(workitems, many=True).data
            return Response({'workitem': items})
        else:
            return JsonErrorResponse(WORK_NOT_FOUND)

    def partial_update(self, request, work_pk, pk):
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        data = request.data.get('workitem', {})
        profile = request.user.profile
        try:
            work = Work.objects.live().get(pk=work_pk, profile=profile)
            workitem = Workitem.objects.get(work=work, pk=pk)
        except ObjectDoesNotExist as e:
            return JsonErrorResponse(GENERIC_NOT_FOUND, status=404)
        serializer = WorkitemSerializer(data=data)
        if serializer.is_valid():
            workitem = serializer.create_or_update(serializer.validated_data,
                                                   work, workitem)
            workitem_data = WorkitemSerializer(workitem).data
            return Response({'workitem': workitem_data})
        else:
            print (serializer.errors)
            return JsonErrorResponse(serializer.errors)

    def destroy(self, request, work_pk, pk):
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        data = request.data.get('workitem', {})
        profile = request.user.profile
        try:
            work = Work.objects.live().get(pk=work_pk, profile=profile)
            workitem = Workitem.objects.get(work=work, pk=pk)
        except ObjectDoesNotExist as e:
            return JsonErrorResponse(GENERIC_NOT_FOUND, status=404)
        workitem.delete()
        return Response(status=204)

    def update(self, request, pk):
        raise Exception('Not implemented')

    def retrieve(self, request, pk):
        raise Exception('Not implemented')


class CommentAPIViewSet(viewsets.ModelViewSet):
    model = Comment

    def get_queryset(self, work_pk):
        work = Work.objects.published().get(pk=work_pk)
        return work.comments.select_related('profile').filter(deleted=False)

    def update(self, request, work_pk, pk):
        raise Exception('Not implemented')

    def retrieve(self, request, work_pk, pk):
        raise Exception('Not implemented')

    def list(self, request, work_pk):
        try:
            comments = self.get_queryset(work_pk)
        except ObjectDoesNotExist as e:
            return Response({'comment': []})
        return Response({'comment': CommentSerializer(comments,
                        many=True).data})

    def destroy(self, request, work_pk, pk):
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        profile = request.user.profile
        try:
            comment = self.get_queryset(work_pk).get(pk=pk)
        except ObjectDoesNotExist as e:
            return JsonErrorResponse(GENERIC_NOT_FOUND, status=404)
        if comment.profile == profile:
            comment.delete()
            return Response(status=204)
        else:
            return JsonErrorResponse(UNAUTHORIZED, status=403)

    def partial_update(self, request, work_pk, pk):
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
        profile = request.user.profile
        try:
            comment = self.get_queryset(work_pk).get(pk=pk)
        except ObjectDoesNotExist as e:
            return JsonErrorResponse(GENERIC_NOT_FOUND, status=404)
        if comment.profile != profile:
            return JsonErrorResponse(UNAUTHORIZED, status=403)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.update(serializer.validated_data, comment)
            return Response({'comment': CommentSerializer(comment).data},
                            status=200)
        else:
            return JsonErrorResponse(serializer.errors)

    def create(self, request, work_pk):
        if not request.user.is_authenticated():
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN)
        profile = request.user.profile
        try:
            work = Work.objects.published().get(pk=work_pk)
        except ObjectDoesNotExist as e:
            return JsonErrorResponse(WORK_NOT_FOUND)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.create(serializer.validated_data,
                                        profile, work)
            return Response({'comment': CommentSerializer(comment).data},
                            status=200)
        else:
            return JsonErrorResponse(serializer.errors)
