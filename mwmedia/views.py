from django.shortcuts import render

from django.http import Http404
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import authentication, permissions

import boto3
import botocore
import hashlib
import logging

from .models import MediaFile

logger = logging.getLogger('meanwise_backend.%s' % __name__)

class MediaUploadView(APIView):

    def put(self, request, filename):
        s3 = boto3.client('s3')

        is_multipart = request.content_type.find('multipart/form-data') != -1
        if is_multipart:
            the_file = request.FILES['media_file']
        else:
            raise Exception("Haven't implemented binary streaming %s" % request.content_type)

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        try:
            md5sum = s3.head_object(Bucket=bucket_name, Key=filename)['ETag'][1:-1]
            m = hashlib.md5()
            for chunk in the_file.chunks(2**20):
                m.update(chunk)
            the_file.file.seek(0)
            if md5sum != m.hexdigest():
                raise Exception("The two files are not the same. You cannot replace existing files.")
            else:
                try:
                    media = MediaFile.objects.get(filename=filename)
                except MediaFile.DoesNotExist:
                    media = MediaFile(filename=filename, storage=MediaFile.STORAGE_S3)

                return Response(
                    {
                        'status': 'success',
                        'error': None,
                        'results': {
                            'message': 'File already exists.',
                            'location': self.get_absolute_url(media)
                        }
                    },
                    status.HTTP_200_OK,
                    headers={ 'Location': self.get_absolute_url(media) }
                )
        except botocore.exceptions.ClientError:
            pass

        response = s3.put_object(
            ACL='public-read',
            Bucket=bucket_name,
            Body=the_file,
            Key=filename,
        )

        media = MediaFile(filename=filename, storage=MediaFile.STORAGE_S3)
        media.save()

        return Response(
            {
                'status': 'success',
                'error': None,
                'results': {
                    'message': 'File successfully uploaded.',
                    'location': self.get_absolute_url(media)
                }
            },
            status.HTTP_200_OK,
            headers={ 'Location': self.get_absolute_url(media) }
        )

    def get_absolute_url(self, media):
        domain = settings.AWS_S3_CUSTOM_DOMAIN
        if domain is None:
            domain = 'https://%s.s3.amazonaws.com' % (settings.AWS_STORAGE_BUCKET_NAME,)

        return '%s/%s' % (domain, media.filename)
