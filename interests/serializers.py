from rest_framework import serializers

from .models import Interest


class ProfileInterestSerializer(serializers.ModelSerializer):
    colorCode = serializers.CharField(source='color_code')
    coverPhoto = serializers.CharField(source='cover_photo_url')

    class Meta:
        model = Interest
        fields = ('id', 'name', 'slug', 'description',
                  'colorCode', 'coverPhoto',)
        read_only_fields = ('name', 'slug', 'description',
                            'colorCode', 'coverPhoto',)


class UpdateProfileInterestSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=False)
