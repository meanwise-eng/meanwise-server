from __future__ import absolute_import, unicode_literals

import os
import logging
import tempfile
import uuid
import random
import boto3

from django.conf import settings

from meanwise_backend.celery import app

from .models import UserVerification
from mwmedia.models import MediaFile

logger = logging.getLogger('meanwise_backend.%s' % __name__)

@app.task(bind=True)
def add_user_verification_photo_to_face_detection_model(self, profile_id):
    def do_retry(ex):
        logger.error(ex)
        raise self.retry(ex=ex, countdown=(random.uniform(2, 4) ** self.request.retries))
    try:
        user_verification = UserVerification.objects.get(id=profile_id)
    except UserVerification.DoesNotExist as ex:
        do_retry(ex)

    try:
        user_verification.add_to_face_detection_model()
    except Exception as ex:
        do_retry(ex)
