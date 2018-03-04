from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from django.urls import reverse

from common.api_helper import build_absolute_uri

from .models import College


class CollegeSerializer(serializers.ModelSerializer):

    students = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = College
        exclude = ('created_on', 'modified_on')

    def get_students(self, obj):
        return build_absolute_uri(reverse('college-students', kwargs={'college_id': obj.id}))

    def get_posts(self, obj):
        return build_absolute_uri(reverse('college-posts', kwargs={'college_id': obj.id}))
