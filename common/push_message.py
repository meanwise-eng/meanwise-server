import logging

from scarface.models import Device, PushMessage

from mnotifications.models import ASNSDevice

from django.conf import settings

logger = logging.getLogger('meanwise_backend.%s' % __name__)


def find_user_devices(user_id):
    """
    Find devices related to user

    """
    devs = ASNSDevice.objects.filter(user_id=int(user_id))
    d = []
    for dev in devs:
        d.append(dev.device)
    return d


def send_message_device(device, message_payload):
    """
    Send message with payload to given device

    """
    message = message_payload['message']
    extra_pload = {
        'p': message_payload['p'],
        'u': message_payload['u'],
        't': message_payload['t']
    }
    try:
        message = PushMessage(badge_count=1, context='url_alert', context_id='none',
                              has_new_content=True, message=message, sound="default",
                              extra_payload=extra_pload)
    except Exception as e:
        logger.error(e)
        return 0
    try:
        device.send(message, extra_pload={'p': message_payload[
                    'p'], 'u': message_payload['u'], 't': message_payload['t']})
    except Exception as e:
        logger.error(e)
        return 0
