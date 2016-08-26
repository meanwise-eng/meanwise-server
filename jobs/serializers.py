from rest_framework import serializers

from jobs.models import Job, JobApplication
from account_profile.models import Profile


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        exclude = ('id',)


class JobAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        excluse = ('id',)


class CandidateViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('id',)
