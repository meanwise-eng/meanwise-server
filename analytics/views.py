from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import SeenPostSerializer, SeenPostBatchSerializer
from post.models import Post
from userprofile.models import UserProfile
from .models import SeenPostBatch


class PostAnalyticsView(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        user_id = data["posts"][0]["user_id"]
        post_id = data["posts"][0]["post_id"]

        try:
            userprofile = UserProfile.objects.get(user__id=user_id)

            try:
                post = Post.objects.get(id=post_id)
                serializer = SeenPostBatchSerializer(data=data)

                if serializer.is_valid():
                    post_batch = serializer.save()
                    return Response({"status": "success", "error": "", "results": "successfully added data"}, status=status.HTTP_200_OK)

                return Response({
                    "status": "failed",
                    "error": {
                        "message": "Error occured on server.",
                        "code": 500,
                        "subCode": 1,
                        "errorTitle": "Error occured on server",
                        "errorMessage": "An unidentified error occured on server. We will be looking into this issue. Please try again later."
                    },
                    "results": ""},
                    status=status.HTTP_501_NOT_IMPLEMENTED)

            except Post.DoesNotExist:
                return Response({
                    "status": "failed",
                    "error": {
                        "message": "Error occured on server.",
                        "code": 500,
                        "subCode": 1,
                        "errorTitle": "Error occured on server",
                        "errorMessage": "An unidentified error occured on server. We will be looking into this issue. Please try again later."
                    },
                    "results": ""},
                    status=status.HTTP_501_NOT_IMPLEMENTED)


        except UserProfile.DoesNotExist:
            return Response({
                "status": "failed",
                "error": {
                    "message": "Error occured on server.",
                    "code": 500,
                    "subCode": 1,
                    "errorTitle": "Error occured on server",
                    "errorMessage": "An unidentified error occured on server. We will be looking into this issue. Please try again later."
                },
                "results": ""},
                status=status.HTTP_501_NOT_IMPLEMENTED)

    def get(self, request):
        post_batch = SeenPostBatch.objects.all()

        serializer = SeenPostBatchSerializer(post_batch, many=True)
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {"seen_posts": serializer.data}
            },
            status=status.HTTP_200_OK
        )
