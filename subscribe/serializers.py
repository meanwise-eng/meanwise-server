from rest_framework import serializers

from account_profile.fields import UsernameField
from account_profile.models import Profile

from .models import Invite


class InviteSerializer(serializers.ModelSerializer):
    username = UsernameField([Invite, Profile],
                             required=False,
                             max_length=25, min_length=3)

    class Meta:
        model = Invite
        fields = ('email', 'username',)
