from common.preparers import DefaultPreparer

from .models import SocialAccount


class UserPreparer(DefaultPreparer):
    model = SocialAccount
    model_type = 'user'
    # attributes = ['email', ]
