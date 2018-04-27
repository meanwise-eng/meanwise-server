import boto3
import uuid

from django.db import models
from django.conf import settings

from mwmedia.models import MediaFile


class UserVerification(models.Model):

    id = models.UUIDField(primary_key=True)
    face_id = models.UUIDField(null=True)
    visual_check_image = models.CharField(max_length=255)
    profile_created = models.BooleanField(default=False)
    probability = models.FloatField()
    match = models.BooleanField()
    match_id = models.UUIDField(null=True)
    audio_captcha_sentence = models.CharField(default=None, max_length=100, null=True)
    audio_captcha_result = models.NullBooleanField(default=None, null=True)
    user_verification_video = models.CharField(max_length=255, null=True, default=None)

    def add_to_face_detection_model(self):
        media = MediaFile.objects.get(filename=self.visual_check_image)
    
        rekog = boto3.client('rekognition', settings.AWS_REGION_NAME)
        collection_id = settings.USERVERIFICATION_COLLECTION_ID
        image = {'S3Object': {'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Name': media.filename}}

        try:
            res = rekog.index_faces(CollectionId=collection_id, Image=image,
                                    ExternalImageId=str(self.id))
        except rekog.exceptions.ResourceNotFoundException:
            res = rekog.create_collection(CollectionId=collection_id)
            res = rekog.index_faces(CollectionId=collection_id, Image=image,
                                    ExternalImageId=str(self.id))

        self.face_id = uuid.UUID(res['FaceRecords'][0]['Face']['FaceId'])
        self.profile_created = True
        self.save()
