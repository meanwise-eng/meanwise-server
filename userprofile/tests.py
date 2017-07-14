import json

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import Profession, Skill, Interest, UserProfile, InviteGroup


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

        # First create a new user
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

    # Create User Profile
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

        self.assertEqual(201, response.status_code)


class ChangePasswordTestCase(APITestCase):

    # Create User Profile
    def create_profile(self):
        url = reverse("register_user")
        data = {
            "username": "test2",
            "email": "test2@gmail.com",
            "password": "password1234",
            "first_name": "testerr",
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

    def test_change_password(self):
        profile_data = self.create_profile()
        self.token = profile_data["results"]["auth_token"]
        self.user_id = profile_data["results"]["user"]

        url = reverse("change-password", kwargs={"user_id": self.user_id})
        data = {
            "old_password": "password1234",
            "new_password": "testpass123"
        }
        response = self.client.post(url, data,
                                    HTTP_AUTHORIZATION='Token {}'.format(self.token),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.user_id, response.data["results"]["id"])


class ForgetPasswordTestCase(APITestCase):

    url = reverse("forget-password")

    def test_forget_password(self):
        # first create a user
        self.username = "testcase"
        self.email = "test@example.com"
        self.password = "password123"
        user = User.objects.create(username=self.username,
                                   email=self.email)
        user.set_password(self.password)
        user.save()

        data = {
            "email": self.email
        }

        response = self.client.post(self.url, data,
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(response.data["results"], "Successfully sent email with new password")
        self.assertEqual(400, response.status_code)


class FriendListTestCase(APITestCase):

    def create_profile(self, username, email):
        url = reverse("register_user")
        data = {
            "username": username,
            "email": email,
            "password": "password1234",
            "first_name": "testerr",
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

    def test_add_friend(self):

        """
        Test to add a new friend and get friend list
        """

        #  create user 1
        user_1 = self.create_profile("test123", "test@example.com")
        self.token_1 = user_1["results"]["auth_token"]
        self.user_id_1 = user_1["results"]["user"]

        # create user 2
        user_2 = self.create_profile("test1231", "test2@gmail.com")
        self.token_2 = user_1["results"]["auth_token"]
        self.user_id_2 = user_2["results"]["user"]

        # url with which user 1 sends a request
        url_1 = reverse("friend", kwargs={"user_id": self.user_id_1})

        # url with which user 2 sends a request
        url_2 = reverse("friend", kwargs={"user_id": self.user_id_2})

        # send friend request to user 2
        data = {
            "friend_id": self.user_id_2,
            "status": "pending"
        }
        response = self.client.post(url_1, data,
                                    HTTP_AUTHORIZATION='Token {}'.format(self.token_1),
                                    headers={
                                       "Content-Type": "application/json"
                                    })
        self.assertEqual(201, response.status_code)

        # accept a friend request of user 1
        data = {
            "friend_id": self.user_id_1,
            "status": "accepted"
        }

        response = self.client.post(url_2, data,
                                    HTTP_AUTHORIZATION='Token {}'.format(self.token_2),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(201, response.status_code)

        # to check if a user is not sending request to himself
        self.assertTrue(self.user_id_1 != self.user_id_2)


        """ 
            Test for getting friend list.
        """

        get_response = self.client.get(url_1,
                                       HTTP_AUTHORIZATION='Token {}'.format(self.token_1),
                                       headers={
                                            "Content-Type": "application/json"
                                       })
        self.assertEqual(200, get_response.status_code)
        self.assertTrue(len(get_response.data["results"]["data"]) >= 1)

    def test_reject_friend(self):
        """
        test to reject a friend request
        """

        # create user 1
        user_1 = self.create_profile("test12331", "test1@example.com")
        self.token_1 = user_1["results"]["auth_token"]
        self.user_id_1 = user_1["results"]["user"]

        # create user 2
        user_2 = self.create_profile("test12312", "test4@gmail.com")
        self.token_2 = user_1["results"]["auth_token"]
        self.user_id_2 = user_2["results"]["user"]

        # url with which user 1 send a request
        url_1 = reverse("friend", kwargs={"user_id": self.user_id_1})

        # url with which user 2 send a request
        url_2 = reverse("friend", kwargs={"user_id": self.user_id_2})

        # send friend request to user 2
        data = {
            "friend_id": self.user_id_2,
            "status": "pending"
        }
        response = self.client.post(url_1, data,
                                    HTTP_AUTHORIZATION='Token {}'.format(self.token_1),
                                    headers={
                                       "Content-Type": "application/json"
                                    })
        self.assertEqual(201, response.status_code)

        # reject friend request of user 1
        data = {
            "friend_id": self.user_id_1,
            "status": "rejected"
        }

        response = self.client.post(url_2, data,
                                    HTTP_AUTHORIZATION='Token {}'.format(self.token_2),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(201, response.status_code)

    def test_request_yourself(self):

        """
        Test to check if user can send a request to himself
        """

        # create user
        user = self.create_profile("test123312", "test12@example.com")
        self.token = user["results"]["auth_token"]
        self.user_id = user["results"]["user"]

        # url with which user 1 send a request
        url = reverse("friend", kwargs={"user_id": self.user_id})

        data = {
            "friend_id": self.user_id,
            "status": "pending"
        }

        response = self.client.post(url, data,
                                    HTTP_AUTHORIZATION='Token {}'.format(self.token),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(400, response.status_code)

    # def test_request_again(self):
    #     """
    #     test to check if a user A can send friend request to user B,
    #     after user B has reject the request.
    #     """

    #     # create user 1
    #     user_1 = self.create_profile("test12331", "test1@example.com")
    #     self.token_1 = user_1["results"]["auth_token"]
    #     self.user_id_1 = user_1["results"]["user"]

    #     # create user 2
    #     user_2 = self.create_profile("test12312", "test4@gmail.com")
    #     self.token_2 = user_1["results"]["auth_token"]
    #     self.user_id_2 = user_2["results"]["user"]

    #     # url with which user 1 send a request
    #     url_1 = reverse("friend", kwargs={"user_id": self.user_id_1})

    #     # url with which user 2 send a request
    #     url_2 = reverse("friend", kwargs={"user_id": self.user_id_2})

    #     # send friend request to user 2
    #     data = {
    #         "friend_id": self.user_id_2,
    #         "status": "pending"
    #     }
    #     response = self.client.post(url_1, data,
    #                                 HTTP_AUTHORIZATION='Token {}'.format(self.token_1),
    #                                 headers={
    #                                    "Content-Type": "application/json"
    #                                 })
    #     self.assertEqual(201, response.status_code)

    #     # reject friend request of user 1
    #     data = {
    #         "friend_id": self.user_id_1,
    #         "status": "rejected"
    #     }

    #     response = self.client.post(url_2, data,
    #                                 HTTP_AUTHORIZATION='Token {}'.format(self.token_2),
    #                                 headers={
    #                                     "Content-Type": "application/json"
    #                                 })
    #     self.assertEqual(201, response.status_code)

    #     # send friend request to user 1
    #     data = {
    #         "friend_id": self.user_id_1,
    #         "status": "pending"
    #     }
    #     response = self.client.post(url_2, data,
    #                                 HTTP_AUTHORIZATION='Token {}'.format(self.token_2),
    #                                 headers={
    #                                    "Content-Type": "application/json"
    #                                 })
    #     print(response.data)
    #     self.assertEqual(201, response.status_code)

    #     # accept request of user 1
    #     data = {
    #         "friend_id": self.user_id_2,
    #         "status": "accepted"
    #     }

    #     response = self.client.post(url_1, data,
    #                                 HTTP_AUTHORIZATION='Token {}'.format(self.token_1),
    #                                 headers={
    #                                     "Content-Type": "application/json"
    #                                 })
    #     print(response.data)
    #     self.assertEqual(201, response.status_code)


class RemoveFriendTestCase(APITestCase):

    def create_profile(self, username, email):
        url = reverse("register_user")
        data = {
            "username": username,
            "email": email,
            "password": "password1234",
            "first_name": "testerr",
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

    def test_remove_friend(self):

        #  create user 1
        user_1 = self.create_profile("test123", "test@example.com")
        self.token_1 = user_1["results"]["auth_token"]
        self.user_id_1 = user_1["results"]["user"]

        # create user 2
        user_2 = self.create_profile("test1231", "test2@gmail.com")
        self.token_2 = user_1["results"]["auth_token"]
        self.user_id_2 = user_2["results"]["user"]

        # url with which user 1 sends a request
        url_1 = reverse("friend", kwargs={"user_id": self.user_id_1})

        # url with which user 2 sends a request
        url_2 = reverse("friend", kwargs={"user_id": self.user_id_2})

        # send friend request to user 2
        data = {
            "friend_id": self.user_id_2,
            "status": "pending"
        }
        response = self.client.post(url_1, data,
                                    HTTP_AUTHORIZATION='Token {}'.format(self.token_1),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(201, response.status_code)

        # accept a friend request of user 1
        data = {
            "friend_id": self.user_id_1,
            "status": "accepted"
        }

        self.client.post(url_2, data,
                         HTTP_AUTHORIZATION='Token {}'.format(self.token_2),
                         headers={
                             "Content-Type": "application/json"
                         })

        # remove a friend
        url = reverse("remove-friend", kwargs={"user_id": self.user_id_2})

        response = self.client.post(url,
                                    HTTP_AUTHORIZATION='Token {}'.format(self.token_2),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(201, response.status_code)


class ValidateCodeTestCase(APITestCase):
    """
    Test case for ValidateInviteCode View
    """

    def create_profile(self):
        url = reverse("register_user")
        data = {
            "username": "test10",
            "email": "test10@gmail.com",
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

    def test_validate_invite(self):
        user_profile = self.create_profile()
        self.token = user_profile["results"]["auth_token"]

        InviteGroup.objects.create(
            name="XYZ",
            invite_code="REALPEOPLE",
        )
        url = reverse("validate-invite")
        data = {
            "invite_code": "REALPEOPLE"
        }

        response = self.client.post(url, data,
                                    HTTP_AUTHORIZATION='Token {}'.format(self.token),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(200, response.status_code)


class SetInviteCodeTestCase(APITestCase):
    """
    Test case for ValidateInviteCode View
    """

    def create_profile(self):
        url = reverse("register_user")
        data = {
            "username": "test11",
            "email": "test11@gmail.com",
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

    def test_set_invite(self):
        user_profile = self.create_profile()
        self.token = user_profile["results"]["auth_token"]

        url = reverse("set-invite")
        data = {
            "invite_code": "REALPEOPLE"
        }

        response = self.client.post(url, data,
                                    HTTP_AUTHORIZATION='Token {}'.format(self.token),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(200, response.status_code)