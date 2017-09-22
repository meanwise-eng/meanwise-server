import json
import string

from time import sleep

from itertools import islice

from test.support import EnvironmentVarGuard
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.models import SlugField
from django import forms

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import serializers

from hypothesis.extra.django.models import models, add_default_field_mapping
from hypothesis.extra.django import TestCase as HTestCase
import hypothesis.strategies as st
from hypothesis import given, assume, example
from meanwise_backend.test_case import GabbiHypothesisTestCase

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
            "text": "test data 234",
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
        query_set = Story.objects.filter(main_post_id=post_id)
        story_id = query_set.values()[0]["id"]
        url = reverse("post-story", kwargs={"story_id": story_id})

        response = self.client.get(url,
                                   HTTP_AUTHORIZATION='Token {}'.format(
                                       token),
                                   headers={
                                       "Content-Type": "application/json"
                                   })

        self.assertEqual(200, response.status_code)


class UserHomeFeedTestCase(APITestCase):
    """
    Test case for home feed
    """

    def create_user(self):
        url = reverse("register_user")
        data = {
            "username": "test0101",
            "email": "test0101@gmail.com",
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
            "token": token,
            "user_id": id
        })

    def test_home_feed(self):
        post = self.create_post()
        user_id = post["user_id"]
        token = post["token"]

        url = reverse("home-feed", kwargs={"user_id": user_id})

        response = self.client.get(url,
                                   HTTP_AUTHORIZATION='Token {}'.format(
                                       token),
                                   headers={
                                       "Content-Type": "application/json"
                                   })
        self.assertEqual(200, response.status_code)


class PublicFeedTestCase(APITestCase):
    """
    Test case for public feed
    """

    def test_public_feed(self):
        url = reverse("public-feed")

        response = self.client.get(url,
                                   headers={
                                       "Content-Type": "application/json"
                                   })
        self.assertEqual(200, response.status_code)


class PostLikeUnlikeTestCase(APITestCase):
    """
    Test case for post like and unlike
    """

    def create_user(self):
        url = reverse("register_user")
        data = {
            "username": "test01010",
            "email": "test01001@gmail.com",
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
            "token": token,
            "user_id": id
        })

    def test_post_like_unlike(self):
        post = self.create_post()
        user_id = post["user_id"]
        token = post["token"]
        post_id = post["post_id"]

        """
        Test for liking a post
        """
        url = reverse(
            "post-like", kwargs={"user_id": user_id, "post_id": post_id})

        response = self.client.post(url,
                                    HTTP_AUTHORIZATION='Token {}'.format(
                                        token),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(202, response.status_code)

        """
        Test for unliking a post
        """
        url = reverse(
            "post-unlike", kwargs={"user_id": user_id, "post_id": post_id})

        response = self.client.post(url,
                                    HTTP_AUTHORIZATION='Token {}'.format(
                                        token),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(202, response.status_code)


class PostComment2TestCase(APITestCase):

    def setUp(self):
        super().setUp()
        self.interest = Interest(name="Travel", slug="travel")
        self.interest.save()
        self.user = User.objects.create(username="tester",
                                        password="password",
                                        email="tester@example.com")
        self.post = Post(poster=self.user, text="Test", interest=self.interest)
        self.post.save()

        self.token = Token.objects.get(user=self.user)
        self.token.save()

    def tearDown(self):
        self.token.delete()
        self.post.delete()
        self.user.delete()
        self.interest.delete()
        super().tearDown()

    @given(st.text(alphabet=st.characters(max_codepoint=1000, blacklist_categories=('Cc', 'Cs')), min_size=1))
    def test_create_post(self, comment_text):
        assume(comment_text is not None and comment_text.strip() != '' and comment_text != '0')
        post_id = self.post.id
        user_id = self.user.id
        token = self.token.key
        """
        Test to post a comment
        """
        url = reverse(
            "post-comment", kwargs={"post_id": post_id})

        comment = {
            "post": post_id,
            "commented_by": user_id,
            "comment_text": comment_text
        }

        #self.run_gabi({
        #    'tests': [{
        #        'name': 'create comment',
        #        'url': url,
        #        'method': 'POST',
        #        'status': 201,
        #        'request_headers': {
        #            'content-type': 'application/json',
        #            'authorization': 'Token %s' % token
        #        },
        #        'data': comment
        #    }]
        #})
        response = self.client.post('%s' % (url,), comment,
                                    HTTP_AUTHORIZATION='Token {}'.format(
                                        token),
                                    headers={
                                        "Content-Type": "application/json",
                                        "Authorization": "Token {}".format(token)
                                    })
        self.assertEqual(201, response.status_code, response.data)
        comment_id = response.data["results"]["id"]
#
        # """
        # Test to list comments of a post
        # """
#
        url = reverse("post-comment", kwargs={"post_id": post_id})

        response = self.client.get(url,
                                   HTTP_AUTHORIZATION='Token {}'.format(
                                       token),
                                   headers={
                                       "Content-Type": "application/json"
                                   })
        self.assertEqual(200, response.status_code)
        field = serializers.CharField()
        text = field.to_representation(comment_text).strip()
        print([repr(c["comment_text"]) for c in response.data['results']['data']], 'v: {}'.format(repr(text)))
        self.assertTrue(text in [c["comment_text"] for c in response.data['results']['data']])

        # """
        # Test to delete a comment
        # """
        url = reverse("comment-detail",
                      kwargs={"post_id": post_id, "comment_id": comment_id})
        response = self.client.delete(url,
                                      HTTP_AUTHORIZATION='Token {}'.format(
                                          token),
                                      headers={
                                          "Content-Type": "application/json"
                                      })
        self.assertEqual(202, response.status_code)

        url = reverse("post-comment", kwargs={"post_id": post_id})
        response = self.client.get(url,
                                   HTTP_AUTHORIZATION='Token {}'.format(
                                       token),
                                   headers={
                                       "Content-Type": "application/json"
                                   })
        self.assertEqual(200, response.status_code)
        self.assertTrue(len(response.data['results']['data']) == 0)


class PostCommentTestCase(APITestCase):
    """
    Test case for posting a comment on post
    """

    def create_user(self):
        url = reverse("register_user")
        data = {
            "username": "test1010",
            "email": "test1001@gmail.com",
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
            "token": token,
            "user_id": id
        })

    def test_post_comment(self):
        post = self.create_post()
        user_id = post["user_id"]
        token = post["token"]
        post_id = post["post_id"]

        """
        Test to post a comment
        """
        url = reverse(
            "post-comment", kwargs={"post_id": post_id})

        comment = {
            "post": post_id,
            "commented_by": user_id,
            "comment_text": "Comment test"
        }

        response = self.client.post(url, comment,
                                    HTTP_AUTHORIZATION='Token {}'.format(
                                        token),
                                    headers={
                                        "Content-Type": "application/json"
                                    })
        self.assertEqual(201, response.status_code)
        comment_id = response.data["results"]["id"]

        """
        Test to list comments of a post
        """

        url = reverse("post-comment", kwargs={"post_id": post_id})

        response = self.client.get(url,
                                   HTTP_AUTHORIZATION='Token {}'.format(
                                       token),
                                   headers={
                                       "Content-Type": "application/json"
                                   })
        self.assertEqual(200, response.status_code)

        """
        Test to delete a comment
        """

        url = reverse("comment-detail",
                      kwargs={"post_id": post_id, "comment_id": comment_id})

        response = self.client.delete(url,
                                      HTTP_AUTHORIZATION='Token {}'.format(
                                          token),
                                      headers={
                                          "Content-Type": "application/json"
                                      })

        self.assertEqual(202, response.status_code)
