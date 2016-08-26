from rest_framework import serializers

from company.serializers import CompanySerializer

from .models import Leader, Page

class LeaderSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    class Meta:
        model = Leader
        exclude = ('id',)

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        exclude = ('id', 'video')
