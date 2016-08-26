from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from common.validators import ExcludeWordsValidator, NotDigitValidator

from .constants import INVALID_USERNAME_UNIQUE, INVALID_USERNAME_REGEX, \
        INVALID_USERNAME_MAX_LENGTH, INVALID_USERNAME_MIN_LENGTH, EXCLUDED_USERNAMES


class UsernameField(serializers.RegexField):
    default_error_messages = {
        'invalid': INVALID_USERNAME_REGEX,
        'max_length': INVALID_USERNAME_MAX_LENGTH,
        'min_length': INVALID_USERNAME_MIN_LENGTH
    }

    def __init__(self, cls, **kwargs):
        regex = '^(?![_.])(?!.*[_.]{2})[a-z0-9._]+(?<![_.])$'
        super(UsernameField, self).__init__(regex, **kwargs)
        self.validators.append(NotDigitValidator())
        self.validators.append(ExcludeWordsValidator(
                    words=EXCLUDED_USERNAMES
                )
            )
        if not isinstance(cls, list): cls = [cls]
        for c in cls:
            self.validators.append(
                UniqueValidator(
                    queryset=c.objects.all(),
                    message=INVALID_USERNAME_UNIQUE
                )
            )
