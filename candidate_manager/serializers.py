from rest_framework import serializers
from account_profile.models import Profile

class CandidateViewSerializer(serializers.ModelSerializer):
	class Meta:
		model = Profile
		exclude = ('id' ,)