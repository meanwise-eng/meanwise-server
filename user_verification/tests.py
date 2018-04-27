import json
import uuid
import hashlib
import boto3

from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from user_verification.models import UserVerification
from user_verification.tasks import add_user_verification_photo_to_face_detection_model

client = APIClient()


class UserVerificationTest(TestCase):

    def setUp(self):
        self.to_delete = []
        self.media_id = 'user-verification/visual-check/%s' % (str(uuid.uuid4()))
        with open('user_photo.jpg', 'rb') as user_photo:
            m = hashlib.md5()
            while True:
                chunk = user_photo.read(2**20)
                if chunk == b"":
                    break
                m.update(chunk)
            user_photo.seek(0)
            md5_hash = m.hexdigest()
            
            client.put('/api/v4/media/upload/%s' % self.media_id, HTTP_X_FILE_HASH=md5_hash, data={'media_file': user_photo})

        self.rekog = boto3.client('rekognition', settings.AWS_REGION_NAME)

    def tearDown(self):
        face_ids = []
        for user_verification in UserVerification.objects.all():
            if user_verification.face_id is not None:
                face_ids.append(user_verification.face_id)
            user_verification.delete()

        if len(face_ids) > 0:
            collection_id = settings.USERVERIFICATION_COLLECTION_ID
            self.rekog.delete_faces(CollectionId=collection_id, FaceIds=face_ids)

    def test_user_verification_shows_no_duplicate_with_new_person(self):
        profile_id = uuid.uuid4()
        self.to_delete.append(profile_id)
        response = client.post('/api/v4/user-verification/', data={'profile_uuid': profile_id,
                               'media_file': self.media_id})

        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertEqual(json['results']['probability'], 0)

        user_verification = UserVerification.objects.get(id=profile_id)
        user_verification.add_to_face_detection_model()

    def test_user_verification_shows_duplicate_with_existing_person(self):
        profile_id = uuid.uuid4()
        response = client.post('/api/v4/user-verification/', data={
            'profile_uuid': profile_id,
            'media_file': self.media_id,
        })

        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertTrue(json['results']['probability'] >= 99)
