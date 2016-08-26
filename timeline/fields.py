from rest_framework import serializers

from account_profile.models import Profession
from account_profile.serializers import ProfessionSerializer
from company.models import Company
from company.serializers import CompanySerializer
from geography.models import Location
from geography.serializers import LocationSerializer

from .models import CourseMajor, Degree


class EventInfoRelatedField(serializers.JSONField):
    '''
    Custom field for Event info
    '''
    def to_representation(self, value):
        '''
        Serialize info objects to a simple textual representation
        '''
        # To prevent circular import
        from .serializers import DegreeSerializer, CourseMajorSerializer
        data = {}
        for k, v in value.iteritems():
            if k == 'company_id':
                data['company'] = Company.cache.get(v, CompanySerializer)
            elif k == 'profession_id':
                data['profession'] = Profession.cache.get(v,
                                                          ProfessionSerializer)
            elif k == 'major_id':
                data['major'] = CourseMajor.cache.get(v, CourseMajorSerializer)
            elif k == 'university_id':
                data['university'] = Location.cache.get(v, LocationSerializer)
            elif k == 'degree_id':
                data['degree'] = Degree.cache.get(v, DegreeSerializer)
            elif k == 'location_id':
                data['location'] = Location.cache.get(v, LocationSerializer)
            else:
                data[k] = v
        return data
