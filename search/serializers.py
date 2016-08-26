from account_profile.serializers import PublicProfileDetailSerializer
from account_profile.models import Profile


class SearchProfileSerializer(PublicProfileDetailSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'username', 'firstName', 'middleName',
                  'lastName', 'message', 'lookingFor', 'profession',
                  'profilePhoto', 'profileViews', 'followerCount',
                  'city', 'likeCount',)
        depth = 2
