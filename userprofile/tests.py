from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import Profession, Skill, Interest, UserProfile


class ProfessionListTestCase(APITestCase):
    """
    Test cases for profession list call
    """

    url = reverse("profession")

    def test_add_profession(self):
        """
        Test to add a Profession
        """
        data = {
            "text": "test profession",
        }

        response = self.client.post(self.url, data,
                                    headers={
                                        'Content-Type': 'application/json'
                                    })
        self.assertEqual(200, response.status_code)

    def test_profession(self):
        """
        Test to verify user created profession
        """
        self.profession = Profession.objects.create(text="Test")

        response = self.client.get(self.url)

        self.assertEqual(
            len(response.data["results"]["data"]), Profession.objects.count()
        )


class SkillListTestCase(APITestCase):
    """
    Test cases for skill list call
    """

    url = reverse("skills")

    def test_add_profession(self):
        """
        Test to add a skill
        """
        data = {
            "text": "test skill",
        }

        response = self.client.post(self.url, data,
                                    headers={
                                        'Content-Type': 'application/json'
                                    })
        self.assertEqual(200, response.status_code)

    def test_profession(self):
        """
        Test to verify user created skill
        """
        self.skill = Skill.objects.create(text="Test")

        response = self.client.get(self.url)

        self.assertEqual(
            len(response.data["results"]["data"]), Skill.objects.count()
        )


class InterestListTestCase(APITestCase):
    """
    Test Case for interest list
    """

    url = reverse("interests")

    def test_interests_list(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_interest(self):
        self.interests = Interest.objects.create(name="Test",
                                                 slug="test",
                                                 description="testing interests",
                                                 topics=["test", "testcase"])
        response = self.client.get(self.url)
        self.assertEqual(
            len(response.data["results"]["data"]), Interest.objects.count()
        )


class ProfileListTestCase(APITestCase):
    """
    Test case for profile list
    """

    url = reverse("profile-list")

    def test_profile_list(self):

        # FIrst create a new user
        self.username = "testcase"
        self.email = "test@example.com"
        self.password = "password123"
        user = User.objects.create(username=self.username,
                                   email=self.email)
        user.set_password(self.password)
        user.save()

        if (user):
            # retrieve its token
            self.token = Token.objects.get(user=user)

        response = self.client.get(self.url, HTTP_AUTHORIZATION=self.token.key)

        self.assertEqual(
            len(response.data["results"]), UserProfile.objects.count()
        )


class ProfileDetailTestCase(APITestCase):

    def create_profile(self):
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
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        return response.data

    def test_get_profile(self):
        profile_data = self.create_profile()
        self.token = profile_data["results"]["auth_token"]
        self.user_id = profile_data["results"]["user"]

        url = reverse("profile-detail", kwargs={"user_id": self.user_id})
        response = self.client.get(url, HTTP_AUTHORIZATION='Token {}'.format(self.token))

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.user_id, response.data["results"]["id"])

    def test_update_profile(self):
        profile_data = self.create_profile()
        self.token = profile_data["results"]["auth_token"]
        self.user_id = profile_data["results"]["user"]

        updated_data = {
            "dob": "1980-10-30",
            "bio": "test"
        }

        url = reverse("profile-detail", kwargs={"user_id": self.user_id})
        response = self.client.patch(url, updated_data,
                                     HTTP_AUTHORIZATION='Token {}'.format(self.token),
                                     headers={
                                        "Content-type": "application/json"
                                     })
        print(response.data)
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.user_id, response.data["results"]["id"])
