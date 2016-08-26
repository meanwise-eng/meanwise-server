from .models import Activity
from .tasks import create_activity, delete_activity


def create(actor, verb, target=None, action_object=None, is_private=False, data={}):
    create_activity.delay(actor, verb,
                          target, action_object,
                          is_private, data={})


def delete(actor, verb, target=None, action_object=None, is_private=False, data={}):
    delete_activity.delay(actor, verb, target, action_object, is_private, data)
