from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import SeenPostBatchSerializer, SeenPostSerializer
from post.models import Post
from userprofile.models import UserProfile
from .models import SeenPostBatch, SeenPost


class PostAnalyticsView(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        user_id = data["posts"][0]["user_id"]
        post_id = data["posts"][0]["post_id"]

        if (request.user.id != user_id):
            raise PermissionDenied("You cannot see post as other user")

        try:
            UserProfile.objects.get(user__id=user_id)

        except UserProfile.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "error": {
                        "message": "Error occured on server.",
                        "code": 500,
                        "subCode": 1,
                        "errorTitle": "Error occured on server",
                        "errorMessage": "An unidentified error occured on server. We will be looking into this issue. Please try again later."
                    },
                    "results": ""
                },
                status=status.HTTP_501_NOT_IMPLEMENTED
            )

        try:
            Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "error": {
                        "message": "Error occured on server.",
                        "code": 500,
                        "subCode": 1,
                        "errorTitle": "Error occured on server",
                        "errorMessage": "An unidentified error occured on server. We will be looking into this issue. Please try again later."
                    },
                    "results": ""
                },
                status=status.HTTP_501_NOT_IMPLEMENTED
            )

        serializer = SeenPostBatchSerializer(data=data)

        if serializer.is_valid():
            post_batch = serializer.save()
            return Response({"status": "success", "error": "", "results": "successfully added data"}, status=status.HTTP_200_OK)

        return Response(
            {
                "status": "failed",
                "error": {
                    "message": "Error occured on server.",
                    "code": 500,
                    "subCode": 1,
                    "errorTitle": "Error occured on server",
                    "errorMessage": "An unidentified error occured on server. We will be looking into this issue. Please try again later."
                },
                "results": ""
            },
            status=status.HTTP_501_NOT_IMPLEMENTED
        )


class PersonalAnalyticsView(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        if int(user_id) == request.user.id:
            posts = SeenPost.objects.filter(poster=int(user_id))
            print(posts)
            serializer = SeenPostSerializer(posts, many=True)

            return Response(
                {
                    "status": "success",
                    "error": "",
                    "results": {"posts": serializer.data}
                },
                status=status.HTTP_200_OK
            )
