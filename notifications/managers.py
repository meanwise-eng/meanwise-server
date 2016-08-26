import uuid
import json

from django.db import models
from django.utils import timezone

from common.db import redis
from common.utils import timestamp
from stream.constants import VerbType

from .constants import NotificationType


class NotificationManager(models.Manager):

    def create_from_activity(self, activity):
        '''
        This function knows which notification to create from
        an activity. As well as whether to create or not.
        The type is actually determined by activity verb.
        Private activities do not generate notifications.

        returns (notiifcaiton_object, created)
        '''
        if activity.is_private:
            return None, False
        if hasattr(activity.target, 'profile'):
            profile = activity.target.profile
        else:
            profile = activity.target

        if activity.verb == VerbType.FOLLOWED:
            notification_type = NotificationType.FOLLOWED
        elif activity.verb == VerbType.LIKED:
            notification_type = NotificationType.LIKED
        elif activity.verb == VerbType.COMMENTED:
            notification_type = NotificationType.COMMENTED
        else:
            return None, False
        notification = self.model(
                    activity=activity,
                    target=activity.target,
                    type = notification_type,
                    data = activity.data,
                    actor= activity.actor,
                    action_object= activity.action_object,
                    profile=profile
                )
        notification.save()
        return notification, True

    def delete_from_activity(self, activity):
        notifications = self.filter(activity=activity)
        notifications.delete()


class NotificationRedisManager(models.Manager):
    '''
    '''
    def _last_updated_timestamp_key(self, profile):
        return 'notif:profile:%s:lu' % (profile.pk)

    def _profile_notifications_key(self, profile):
        return 'notif:profile:%s:n' % (profile.pk)

    def _notifications_key(self, notification):
        if isinstance(notification, str) or \
                isinstance(notification, unicode) or \
                isinstance(notification, uuid.UUID):
            pk = notification
        else:
            pk = notification.pk
        return 'notif:%s' % (pk)

    def build(self, profile):
        '''
        This function builds notification cache from database.
        But this should not be used a lot, as everything should be present in redis
        all the time.
        '''
        from .serializers import NotificationRedisSerializer
        notifs = self.filter(profile=profile).order_by('created_on')
        for notif in notifs:
            self.add(notif)

    def add(self, notification):
        '''
        This function adds a notification to the cache.
        In all 4 data structures are used to maintain notifications
        1. Key that saves the timestamp of the time notification was last updated.
        2. Set, for saving list of notification uuids
        3. A Key for storing below mentioned json.
        4. This is for actors/action_object/target string/json.

        First update last added key timestamp for this profile

        Then append to list the following structure
        {
            'id'    : '',
            'actor' : <actor-redis-key>,
            'type'  : '<type>',
            'actionObject' :  <action-object-redis-key>,
            'target': <target-redis-key>,
            'created-on' : <timestamp>,
            'read'  : true/false
        }
        '''
        from .serializers import NotificationRedisSerializer
        redis.set(self._last_updated_timestamp_key(notification.profile), timestamp(notification.created_on))
        redis.lpush(self._profile_notifications_key(notification.profile), notification.id)
        notification_data = json.dumps(NotificationRedisSerializer(notification).data)
        redis.set(self._notifications_key(notification.pk), notification_data)

    def delete(self, notification):
        '''
        This function deletes notification.
        First delete from list and then the notification
        '''
        notif_key = self._notifications_key(notification.pk)
        redis.lrem(self._profile_notifications_key(notification.profile), 0, notification.id)
        redis.delete(notif_key)

    def _get_notification(self, notif_id):
        '''
        Get notification basic json via id.
        '''
        notif = redis.get('notif:%s' % notif_id)
        return json.loads(notif) if notif else notif

    def _get_notification_data(self, notif):
        '''
        Get notification data from basic notifi json
        '''
        actor = redis.get(notif['actor'])
        notif['actor'] = json.loads(actor) if actor else actor
        action_object = redis.get(notif['actionObject'])
        notif['actionObject'] = json.loads(action_object) if action_object else action_object
        target = redis.get(notif['target'])
        notif['target'] = json.loads(target) if target else target
        return notif

    def get_by_profile(self, profile, count=10, since=None, till=None):
        '''
        This function is responsible for fetching notifications for a particular profile.
        Notifications are created from activity stream.
        Only a subset of sctivity converts into a notification. To improve
        performance notifications are saved in redis. Whenever an activity is created
        depending on activity a notification is added in redis.
        This function only fetches notifications from redis.
        If notification key is not found in redis for this user, then it should
        fetch notifications from database.

        @params profile user for which notification needs to be fetched
        @params since timestamp, get notifications from current timestamp to <since>
        @params till timestamp, get notifications from till to <count>
        '''
        if till:
            notifications = []
            notification_ids = redis.lrange(
                            self._profile_notifications_key(profile), 0, -1
                        )
            for notif_id in notification_ids:
                notif  = self._get_notification(notif_id)
                if notif['createdOn'] < till:
                    notifications.append(self._get_notification_data(notif))
                if len(notifications) >= count:
                    break
        else:
            notification_ids = redis.lrange(
                        self._profile_notifications_key(profile), 0, count-1
                    )
            notifications = []
            for notif_id in notification_ids:
                notif = self._get_notification(notif_id)
                if (since and notif['createdOn'] > since) or (not since):
                    notif = self._get_notification_data(notif)
                    notifications.append(notif)
        return notifications

    def last_added_by_profile(self, profile):
        '''
        This function fetches the timestamp of last added notification
        for the specified profile
        '''
        ts  = redis.get(self._last_updated_timestamp_key(profile))
        ts = int(ts) if ts else 0
        return ts

    def mark_read(self, notif):
        notif['read'] = True
        redis.set(self._notifications_key(notif['id']), json.dumps(notif))

    def mark_read_bulk(self, notif_ids, profile):
        notification_ids = redis.lrange(
                            self._profile_notifications_key(profile), 0, -1
                        )
        ids = set(notif_ids).intersection(notification_ids)
        for notif_id in ids:
            self.mark_read(self._get_notification(notif_id))
