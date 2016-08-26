from rest_framework import serializers
from company.models import Company, CompanyLocation, CompanyProfile, CompanyCulture

class CompanyCultureSerializer(serializers.ModelSerializer):
	class Meta:
		model = CompanyCulture
		exclude = ('id',)


class CompanyLocationSerializer(serializers.ModelSerializer):
	class Meta:
		model = CompanyLocation
		exclude = ('id',)

class CompanyProfileSerializer(serializers.ModelSerializer):
	offices = CompanyLocationSerializer(many=True, required=False)
	class Meta:
		model = CompanyProfile
		exclude = ('id', 'culture')

class CompanySerializer(serializers.ModelSerializer):
    profile = CompanyProfileSerializer(required=False)
    class Meta:
        model = Company
        exclude = ('id', 'verified',)
