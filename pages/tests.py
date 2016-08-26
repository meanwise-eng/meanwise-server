from django.test import TestCase
from pages.models import Page
from company.models import Company
# Create your tests here.

class PageCreationTestCase(TestCase):
	def setUp(self):
		Company.objects.create(first_name='Tinh', last_name='Nguyen',
							   email='example1@ex.com', phone_number='+41524204242',
							   company_name='cabbage.io', company_size=100,
							   company_description='A new company')
		Company.objects.create(first_name='Billy', last_name='Bob',
							   email='example2@ex.com', phone_number='+41524204243',
							   company_name='blueberri.io', company_size=1,
							   company_description='A newer company')

		Page.objects.create(website='example1.com')
