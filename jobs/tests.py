from django.test import TestCase
from elasticutils.contrib.django.estestcase import ESTestCase

from account_profile.models import Profile, Skill
from company.models import Company

from .models import Job, JobApplication
# Create your tests here.

class JobCreation(TestCase):
	def setUp(self):
		python = Skill.objects.create(text='Python')
		java = Skill.objects.create(text='Java')

		c1 = Company.objects.create(first_name='Tinh', last_name='Nguyen',
							   		email='example1@ex.com', phone_number='+41524204242',
							   		company_name='cabbage.io', company_size=100,
							   		company_description='A new company')
		c2 = Company.objects.create(first_name='Billy', last_name='Bob',
							   		email='example2@ex.com', phone_number='+41524204243',
							   		company_name='blueberri.io', company_size=1,
							   		company_description='A newer company')

		j1 = Job.objects.create(title='Job1', company=c1, compensation='100k', kind='FT')
		j2 = Job.objects.create(title='Job2', company=c2, compensation='1k', kind='PT')

		j1.skills.add(python)

		j2.skills.add(java)
		j2.skills.add(python)

	def testEasyQuery(self):
		"""
		testing for one and multiple query of skills.
		NOTE: add this to 
		"""
		java = Skill.objects.get(text='Java')
		python = Skill.objects.get(text='Python')
		return set(Job.objects.filter(skills__in=[python, java]))


class TestQueries(ESTestCase):
	pass
		
