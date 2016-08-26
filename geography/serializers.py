from rest_framework import serializers

from .models import City, Location


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'city', 'area', 'country', 'description', )


class UpdateProfileCitySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=False)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'city', 'area', 'country', 'description', )


class UpdateProfileLocationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=False)
