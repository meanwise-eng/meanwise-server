from celery import task

from django.contrib.contenttypes.models import ContentType

from notifications.models import Notification

from .models import Activity
from .constants import VerbType


@task
def create_activity(actor, verb, target=None, action_object=None, is_private=False, data={}):
    activity = Activity(actor=actor, verb=verb,
                        target=target, action_object=action_object,
                        is_private=is_private, data=data)
    activity.save()
    # Only an activity should be allowed to create a notification
    if not activity.is_private:
        Notification.objects.create_from_activity(activity)


@task
def delete_activity(actor, verb, target=None, action_object=None, is_private=False, data={}):
    if verb in VerbType.deletable():
        if action_object:
            activity = Activity.objects.get(
                actor_content_type=ContentType.objects.get_for_model(actor),
                actor_object_id=actor.id,
                action_object_content_type=ContentType.objects.get_for_model(action_object),
                action_object_object_id=action_object.id,
                verb=verb,
                target_content_type=ContentType.objects.get_for_model(target),
                target_object_id=target.id
            )
        else:
            activity = Activity.objects.get(
                actor_content_type=ContentType.objects.get_for_model(actor),
                actor_object_id=actor.id,
                verb=verb,
                target_content_type=ContentType.objects.get_for_model(target),
                target_object_id=target.id
            )
        activity.delete()
        if not activity.is_private:
            Notification.objects.delete_from_activity(activity)
