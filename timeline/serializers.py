from rest_framework import serializers

from common.utils import camel_case_to_snake_case
from company.models import Company
from company.serializers import CompanySerializer
from account_profile.models import Profession
from account_profile.serializers import ProfessionSerializer
from geography.serializers import (CitySerializer, LocationSerializer,
                                   UpdateProfileLocationSerializer,
                                   UpdateProfileCitySerializer)

from .models import Event, Degree, CourseMajor
from .constants import EventType
from .fields import EventInfoRelatedField


class DegreeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    text = serializers.CharField(required=False)
    code = serializers.CharField(required=False)

    class Meta:
        model = Degree
        fields = ('id', 'text', 'code',)


class CourseMajorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    text = serializers.CharField(max_length=128, required=False)

    class Meta:
        model = CourseMajor
        fields = ('id', 'text',)


class BaseEventSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=EventType.choices())
    startDay = serializers.IntegerField(source='start_day', required=False)
    startMonth = serializers.IntegerField(source='start_month', required=False)
    startYear = serializers.IntegerField(source='start_year')
    endDay = serializers.IntegerField(source='end_day', required=False)
    endMonth = serializers.IntegerField(source='end_month', required=False)
    endYear = serializers.IntegerField(source='end_year', required=False)
    description = serializers.CharField(required=False)


class EventSerializer(BaseEventSerializer):
    profileId = serializers.IntegerField(source='profile_id')
    city = CitySerializer(required=False)
    info = EventInfoRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'type', 'startDay', 'startMonth', 'startYear',
                  'endDay', 'endMonth', 'endYear', 'ongoing',
                  'description', 'profileId', 'city', 'info',)


class EventUpdateSerializerMixin():
    def create_or_update(self, validated_data, instance=None):
        validated_data.pop('type')
        # Dont set type here.
        from django.db import transaction
        with transaction.atomic():
            if not instance:
                instance = Event()
            instance.profile = self.context['profile']
            instance.type = self.context['type']
            info_data = validated_data.pop('info')
            info_serializer = self.get_info_serializer()(data=info_data)
            if info_serializer.is_valid():
                instance.info = info_serializer.create()
            else:
                raise Exception(info_serializer.errors)

            city_data = validated_data.pop('city')
            instance.city_id = city_data['id']

            for key, value in validated_data.items():
                setattr(instance, camel_case_to_snake_case(key), value)
            if instance.ongoing:
                instance.end_day = instance.end_year = instance.end_month = None
            instance.save()
        return instance


class ProfessionalEventInfoUpdateSerializer(serializers.Serializer):
    company = CompanySerializer()
    profession = ProfessionSerializer()

    def create(self):
        info = {}
        profession_data = self.validated_data.pop('profession')
        company_data = self.validated_data.pop('company')
        info['profession_id'] = Profession.objects.create_or_get_from_data(profession_data).id
        info['company_id'] = Company.objects.create_or_get_from_data(company_data, key='name').id
        return info


class AcademicEventInfoUpdateSerializer(serializers.Serializer):
    degree = DegreeSerializer()
    major = CourseMajorSerializer()
    university = UpdateProfileLocationSerializer()

    def create(self):
        info = {}
        info['degree_id'] = self.validated_data['degree']['id']
        info['university_id'] = self.validated_data['university']['id']
        major_data = self.validated_data.pop('major')
        info['major_id'] = CourseMajor.objects.create_or_get_from_data(major_data).pk
        return info


class OtherEventInfoUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    location = UpdateProfileLocationSerializer()

    def create(self):
        info = {}
        info['title'] = self.validated_data['title']
        info['location_id'] = self.validated_data['location']['id']
        return info


class AchievementEventInfoUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    awarding_body = serializers.CharField(max_length=128)

    def create(self):
        return self.validated_data


class EventEventInfoUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    location = UpdateProfileLocationSerializer()

    def create(self):
        info = {}
        info['title'] = self.validated_data['title']
        info['location_id'] = self.validated_data['location']['id']
        return info


class ProjectEventInfoUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    subtext = serializers.CharField(max_length=128)

    def create(self):
        return self.validated_data


class ProfessionalEventUpdateSerializer(EventUpdateSerializerMixin, BaseEventSerializer):
    info = ProfessionalEventInfoUpdateSerializer()
    city = UpdateProfileCitySerializer()

    class Meta:
        model = Event
        fields = ('id', 'type', 'startDay', 'startMonth',
                  'startYear', 'endDay', 'endMonth', 'endYear',
                  'ongoing', 'description', 'info', 'city',)

    def get_info_serializer(self):
        return ProfessionalEventInfoUpdateSerializer


class AcademicEventUpdateSerializer(EventUpdateSerializerMixin, BaseEventSerializer):
    info = AcademicEventInfoUpdateSerializer()
    city = UpdateProfileCitySerializer()

    class Meta:
        model = Event
        fields = ('id', 'type', 'startDay', 'startMonth',
                  'startYear', 'endDay', 'endMonth', 'endYear',
                  'ongoing', 'description', 'info', 'city',)

    def get_info_serializer(self):
        return AcademicEventInfoUpdateSerializer


class OtherEventUpdateSerializer(EventUpdateSerializerMixin, BaseEventSerializer):
    info = OtherEventInfoUpdateSerializer()
    city = UpdateProfileCitySerializer()

    class Meta:
        model = Event
        fields = ('id', 'type', 'startDay', 'startMonth',
                  'startYear', 'endDay', 'endMonth', 'endYear',
                  'ongoing', 'description', 'info', 'city',)

    def get_info_serializer(self):
        return OtherEventInfoUpdateSerializer


class AchievementEventUpdateSerializer(EventUpdateSerializerMixin, BaseEventSerializer):
    info = AchievementEventInfoUpdateSerializer()
    city = UpdateProfileCitySerializer()

    class Meta:
        model = Event
        fields = ('id', 'type', 'startDay', 'startMonth',
                  'startYear', 'endDay', 'endMonth', 'endYear',
                  'ongoing', 'description', 'info', 'city',)

    def get_info_serializer(self):
        return AchievementEventInfoUpdateSerializer


class EventEventUpdateSerializer(EventUpdateSerializerMixin, BaseEventSerializer):
    info = EventEventInfoUpdateSerializer()
    city = UpdateProfileCitySerializer()

    class Meta:
        model = Event
        fields = ('id', 'type', 'startDay', 'startMonth',
                  'startYear', 'endDay', 'endMonth', 'endYear',
                  'ongoing', 'description', 'info', 'city',)

    def get_info_serializer(self):
        return EventEventInfoUpdateSerializer


class ProjectEventUpdateSerializer(EventUpdateSerializerMixin, BaseEventSerializer):
    info = ProjectEventInfoUpdateSerializer()
    city = UpdateProfileCitySerializer()

    class Meta:
        model = Event
        fields = ('id', 'type', 'startDay', 'startMonth',
                  'startYear', 'endDay', 'endMonth', 'endYear',
                  'ongoing', 'description', 'info', 'city',)

    def get_info_serializer(self):
        return ProjectEventInfoUpdateSerializer
