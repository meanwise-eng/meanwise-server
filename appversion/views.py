from django.http import Http404

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication

from .models import Version, UserVersion
from .serializers import VersionSerializer


class VersionView(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request, platform, version):
        try:
            version = Version.objects.get(version_string=version, platform=platform.lower())
        except Version.DoesNotExist:
            raise Http404

        response = {"status": "success", "error": "", "results": ""}
        responseStatus = status.HTTP_200_OK

        if version.status == Version.STATUS_INACTIVE:
            error = {
                'detail': 'Version %s is obsolete.' % (version.version_string)
            }
            response['status'] = 'failed'
            response['error'] = error
        elif version.status == Version.STATUS_DRAFT:
            error = {
                'detail': 'Version %s is not published.' % (version.version_string)
            }
            response['status'] = 'failed'
            response['error'] = error

        response['results'] = {
            "version": VersionSerializer(version).data,
        }

        if request.user.id:
            try:
                user_version = UserVersion.objects.get(user_id=request.user.id)

                if user_version.version.version_string != version.version_string:
                    user_version.version = version
                    user_version.save()
            except Exception:
                user_version = UserVersion()
                user_version.user_id = request.user.id
                user_version.version = version
                user_version.save()
                pass

        try:
            latest_version = Version.objects.filter(
                status=Version.STATUS_PUBLISHED).latest('version_sort')
            response['results']['latest_version'] = VersionSerializer(latest_version).data
        except Version.DoesNotExist:
            pass

        return Response(response, status=responseStatus)
