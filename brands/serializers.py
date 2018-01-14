from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from django.urls import reverse

from common.api_helper import build_absolute_uri

from .models import Brand
from .documents import BrandDocument


class BrandDocumentSerializer(DocumentSerializer):

    id = serializers.IntegerField(source='_id')

    class Meta:
        document = BrandDocument
        fields = ('id', 'name', 'description', 'logo', 'logo_thumbnail', 'compact_display_image',
                  'profile_image', 'profile_color', 'members', 'posts')


class OrgDocumentSummarySerializer(serializers.Serializer):

    id = serializers.CharField(source='_id')
    name = serializers.CharField()
    compact_display_image = serializers.CharField()
    type = serializers.CharField()
    url = serializers.CharField()


class BrandSerializer(serializers.ModelSerializer):

    members = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        exclude = ('created_on', 'last_update_on')

    def get_members(self, obj):
        return build_absolute_uri(reverse('brand-members', kwargs={'brand_id': obj.id}))

    def get_posts(self, obj):
        return build_absolute_uri(reverse('brand-posts', kwargs={'brand_id': obj.id}))
