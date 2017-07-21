from rest_framework import serializers

from .models import Version

class VersionSerializer(serializers.ModelSerializer):
	version = serializers.CharField(source='version_string')
	class Meta:
		model = Version
		fields = ('version',)
