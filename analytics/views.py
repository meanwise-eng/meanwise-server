import json
from datetime import datetime, timedelta

from django.core.exceptions import PermissionDenied
from django.db.models import Count

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import SeenPostBatchSerializer, SeenPostSerializer
from post.models import Post, Comment
from userprofile.models import UserProfile
from .models import SeenPost


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

    def get(self, request):

        kwargs = {}
        user_id = request.GET.get("user")
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")

        if user_id is not None:
            kwargs['poster'] = int(user_id)

            if date_from is not None:
                kwargs['datetime__gte'] = date_from

            if date_to is not None:
                date_to = datetime.strptime(date_to, "%Y-%m-%d")
                date_to = date_to + timedelta(days=1)
                kwargs['datetime__lte'] = date_to

            if int(user_id) == request.user.id:
                try:
                    UserProfile.objects.get(user__id=int(user_id))

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

                posts = SeenPost.objects.filter(**kwargs)
                serializer = SeenPostSerializer(posts, many=True)
                data = json.loads(json.dumps(serializer.data))

                for i in range(len(data)):
                    post_id = data[i]["post_id"]

                    like_queryset = Post.objects.filter(id=post_id).values("liked_by", likes=Count("liked_by"))
                    likes = (list(like_queryset)[0]["likes"])

                    comment_queryset = Comment.objects.filter(post=post_id)
                    comments = len(list(comment_queryset))

                    data[i]["no_of_likes"] = likes
                    data[i]["no_of_comments"] = comments

                return Response(
                    {
                        "status": "success",
                        "error": "",
                        "results": {"posts": data}
                    },
                    status=status.HTTP_200_OK
                )

            else:
                raise PermissionDenied("You cannot view analytics of other users")

        return Response(
            {
                "status": "failed",
                "error": {
                    "message": "Error occured on server.",
                    "code": 400,
                    "errorTitle": "Bad Request",
                },
                "results": ""
            },
            status=status.HTTP_400_BAD_REQUEST
        )
