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

    def test_facebook_login(self):
        url = reverse("register_user")
        data = {
            "username": "testuser8@test.com",
            "email": "testuser8@test.com",
            "facebook_token": "fbtokeneight",
            "first_name": "testfname8",
            "skills": [],
            "interests": [],
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


class FetchTokenTestCase(APITestCase):
    """
    Test Case for FetchToken View
    """

    def create_user(self):
        url = reverse("register_user")
        data = {
            "username": "test123",
            "email": "test123@gmail.com",
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

        self.client.post(url, data,
                         headers={'Content-Type': 'application/json'})

    def test_fetch_token(self):
        self.create_user()

        url = reverse("fetch-token")
        data = {
            "email": "test123@gmail.com",
            "password": "password123",
        }

        response = self.client.post(url, data,
                                    headers={'Content-Type': 'application/json'})

        self.assertEqual(200, response.status_code)
        self.assertTrue("token" in response.data["result"])

    def test_api_auth_token(self):
        self.create_user()
        url = reverse("api-token")
        data = {
            "username": "test123",
            "password": "password123",
        }

        response = self.client.post(url, data,
                                    headers={'Content-Type': 'application/json'})

        self.assertEqual(200, response.status_code)
        self.assertTrue("token" in response.data)


class VerifyUserTestCase(APITestCase):

    def create_user(self):
        url = reverse("register_user")
        data = {
            "username": "test13",
            "email": "test13@gmail.com",
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

        self.client.post(url, data,
                         headers={'Content-Type': 'application/json'})

    def test_verify_email(self):
        self.create_user()

        url = reverse("verify-email")
        data = {
            "email": "test13@gmail.com",
        }

        response = self.client.post(url, data,
                                    headers={'Content-Type': 'application/json'})

        self.assertEqual(202, response.status_code)

    def test_verify_username(self):

        url = reverse("verify-username")
        data = {
            "username": "test13",
        }

        response = self.client.post(url, data,
                                    headers={'Content-Type': 'application/json'})

        self.assertEqual(202, response.status_code)
