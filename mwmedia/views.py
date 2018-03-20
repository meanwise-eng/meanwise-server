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

        file_md5sum = request.META.get('HTTP_X_FILE_HASH', None)
        md5sum = MediaFile._get_hash(the_file)
        if file_md5sum != md5sum:
            raise Exception("The uploaded file's hash (%s) doesn't match with hash in X-File-Hash (%s)" % (md5sum, file_md5sum))

        try:
            media = MediaFile.create(the_file.file, filename, file_md5sum)
        except MediaFile.FileAlreadyExists:
            return Response(
                {
                    'status': 'success',
                    'error': None,
                    'results': {
                        'message': 'File already exists.',
                        'location': self.get_absolute_url(filename)
                    }
                },
                status.HTTP_200_OK,
                headers={ 'Location': self.get_absolute_url(filename) }
            )

        return Response(
            {
                'status': 'success',
                'error': None,
                'results': {
                    'message': 'File successfully uploaded.',
                    'location': self.get_absolute_url(filename)
                }
            },
            status.HTTP_200_OK,
            headers={ 'Location': self.get_absolute_url(filename) }
        )

    def get_absolute_url(self, filename):
        domain = settings.AWS_S3_CUSTOM_DOMAIN
        if domain is None:
            domain = 'https://%s.s3.amazonaws.com' % (settings.AWS_STORAGE_BUCKET_NAME,)

        return '%s/%s' % (domain, filename)
