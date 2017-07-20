import json
from itertools import islice

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from userprofile.models import Interest
from .models import Story, Post


class UserPostListTestCase(APITestCase):
    """
    Test case for UserPostList View
    """

    def create_user(self):
        url = reverse("register_user")
        data = {
            "username": "test01",
            "email": "test01@gmail.com",
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
                                    headers={"Content-Type": "application/json"})
        return response.data

    def create_interest(self):
        url = reverse("interests")

        self.interests = Interest.objects.create(name="Test",
                                                 slug="test",
                                                 description="testing interests",
                                                 topics=["test", "testcase"])
        response = self.client.get(url)
        data = json.loads(json.dumps(response.data["results"]["data"][0]))
        return data["id"]

    def test_post(self):
        user = self.create_user()
        interest = self.create_interest()
        id = user["results"]["user"]
        token = user["results"]["auth_token"]

        url = reverse("post-list", kwargs={"user_id": id})

        data = {
            "text": "test data",
            "interest": [interest]
        }

        response = self.client.post(url, data,
                                    HTTP_AUTHORIZATION='Token {}'.format(
                                        token),
                                    headers={
                                        "Content-Type": "application/json"
                                    })

        self.assertEqual(201, response.status_code)

        """
        Test to get the post by a user
        """

        response = self.client.get(url,
                                   HTTP_AUTHORIZATION='Token {}'.format(
                                       token),
                                   headers={
                                       "Content-Type": "application/json"
                                   })
        data = response.data["results"]["data"]

        post_id = dict(data[0])["id"]
        self.assertEqual(200, response.status_code)

        """
        Test to delete a post by the user
        """
        url = reverse(
            "post-detail", kwargs={"user_id": id, "post_id": post_id})
        response = self.client.delete(url,
                                      HTTP_AUTHORIZATION='Token {}'.format(
                                          token),
                                      headers={
                                          "Content-Type": "application/json"
                                      })
        self.assertEqual(202, response.status_code)


class UserFriendsPostListTestCase(APITestCase):
    """
    Test to view post of a friend
    """

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

    def test_friends_post(self):
        user = self.create_profile("test002", "test002@example.com")
        token = user["results"]["auth_token"]
        user_id = user["results"]["user"]

        url = reverse("friend-post", kwargs={"user_id": user_id})

        response = self.client.get(url,
                                   HTTP_AUTHORIZATION='Token {}'.format(
                                       token),
                                   headers={
                                       "Content-Type": "application/json"
                                   })

        self.assertEqual(200, response.status_code)


class UserInterestPostList(APITestCase):

    def create_user(self):
        url = reverse("register_user")
        data = {
            "username": "test010",
            "email": "test010@gmail.com",
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
                                    headers={"Content-Type": "application/json"})
        return response.data

    def test_interest_post(self):
        user = self.create_user()
        id = user["results"]["user"]
        token = user["results"]["auth_token"]

        url = reverse("interest-post", kwargs={"user_id": id})

        response = self.client.get(url,
                                   HTTP_AUTHORIZATION='Token {}'.format(
                                       token),
                                   headers={
                                       "Content-Type": "application/json"
                                   })

        self.assertEqual(200, response.status_code)


class StoryDetailTestCase(APITestCase):

    def create_user(self):
        url = reverse("register_user")
        data = {
            "username": "test011",
            "email": "test011@gmail.com",
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
                                    headers={"Content-Type": "application/json"})
        return response.data

    def create_interest(self):
        url = reverse("interests")

        self.interests = Interest.objects.create(name="Test",
                                                 slug="test",
                                                 description="testing interests",
                                                 topics=["test", "testcase"])
        response = self.client.get(url)
        data = json.loads(json.dumps(response.data["results"]["data"][0]))
        return data["id"]

    def create_post(self):
        user = self.create_user()
        interest = self.create_interest()
        id = user["results"]["user"]
        token = user["results"]["auth_token"]

        url = reverse("post-list", kwargs={"user_id": id})

        data = {
            "text": "test data",
            "interest": [interest],
        }

        response = self.client.post(url, data,
                                    HTTP_AUTHORIZATION='Token {}'.format(
                                        token),
                                    headers={
                                        "Content-Type": "application/json"
                                    })

        res_data = response.data["results"]
        return ({
            "post_id": res_data["id"],
            "token": token
        })

    def test_story(self):
        post = self.create_post()
        post_id = post["post_id"]
        token = post["token"]

        post_ins = Post.objects.get(id=post_id)
        Story.objects.create(main_post=post_ins)
        query_set = Story.objects.filter(pk=post_id)
        story_id = query_set.values()[0]["id"]
        url = reverse("post-story", kwargs={"story_id": story_id})

        response = self.client.get(url,
                                   HTTP_AUTHORIZATION='Token {}'.format(
                                       token),
                                   headers={
                                       "Content-Type": "application/json"
                                   })

        self.assertEqual(200, response.status_code)
