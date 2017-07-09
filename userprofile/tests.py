import json

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase

from .models import Profession, Skill


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

    def test_interests(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
