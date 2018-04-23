import json
import uuid
import hashlib
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase, Client
from django.urls import reverse

client = APIClient()


class UserVerificationTest(TestCase):

    def setUp(self):
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

    def test_user_verification_shows_no_duplicate_with_new_person(self):
        profile_id = uuid.uuid4()
        response = client.post('/api/v4/user-verification/', data={'profile_uuid': profile_id,
                               'media_file': self.media_id})

        self.assertEqual(response.status_code, 200)
