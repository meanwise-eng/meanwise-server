from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from rest_framework.exceptions import ValidationError


class ExcludeWordsValidator(object):
    '''
    This validator validates if the specifid value
    exists in a list of words or not. It exists then validation error is raised
    '''
    message = _('This value can not be taken.')

    def __init__(self, words=[], message=None):
        self.words = words
        self.message = message or self.message

    def __call__(self, value):
        if value in self.words:
            raise ValidationError(self.message)


class NotDigitValidator(object):
    '''
    This validator validates if the specifid value is a valid integer or not.
    Raise error if it an integer
    '''
    message = _('The username can not be only digits.')

    def __init__(self, message=None):
        self.message = message or self.message

    def __call__(self, value):
        if value.isdigit():
            raise ValidationError(self.message)


class PasswordValidator(object):
    '''
    This is a common validator for validating password.
    It uses django's own validate_password function
    '''
    message = _('Please enter a valid password')

    def __init__(self):
        pass

    def __call__(self, value):
        validate_password(value)
