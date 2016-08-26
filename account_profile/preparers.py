from common.preparers import DefaultPreparer
from authentication.preparers import UserPreparer

from .models import Profile

class ProfilePreparer(DefaultPreparer):
    model = Profile
    model_type = 'profile'
    attributes = ['first_name', 'middle_name', 'last_name', 'username', 'full_name', 'message', 'description']
    relationships = {
            'user': UserPreparer,
            'profession': DefaultPreparer,
            'skills': DefaultPreparer
        }
