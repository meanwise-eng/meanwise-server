from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse


class UserRegisterationTests(APITestCase):
    """
    For testing user registeration
    """
    def test_new_user(self):
        """
        Ensures we can create a new user
        """
        url = reverse("register_user")
        data = {
            "username": "test",
            "email": "test@gmail.com",
            "password": "password123",
            "first_name": "tester",
            "last_name": "last",
            "skills": [],
            "interests": [],
            "skills_list": [],
            "invite_code": "REALPEOPLE",
            "dob": "2000-10-10",
            "profile_story_title": "sfdsfs",
            "profile_story_description": "dfssfsfs",
            "profile_background_color": "Blue"
        }

        response = self.client.post(url, data,
                                    headers={'Content-Type': 'application/json'})
        self.assertEqual(201, response.status_code)
        self.assertTrue("auth_token" in response.data["results"])
