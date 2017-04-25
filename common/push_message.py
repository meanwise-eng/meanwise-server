from scarface.models import *

from django.conf import settings


def find_user_devices(user_id):
    """
    Find devices related to user

    """
    devices = Devices.object.filter(device_id__startswith==str(user_id))
    return devices
    
def send_message_device(device, message_payload):
    """
    Send message with payload to given device

    """
    if device.platform.name in ["APNS_SANDBOX", "APNS"]:
        apns_dict = {'aps':{'alert':message_payload['message'],'p':message_payload[p], 'u':message_payload['u'],'t':message_payload['t']}}
        apns_string = json.dumps(apns_dict,ensure_ascii=False)
        if device.platform.name in ["APNS_SANDBOX"]:
            message = {'default':message_payload['message'],'APNS_SANDBOX':apns_string}
        else:
            message = {'default':message_payload['message'],'APNS':apns_string}
        messageJSON = json.dumps(message,ensure_ascii=False)
    elif device.platform.name in ["GCM"]:
        apns_dict = {'gcm':{'alert':message_payload['message'],'p':message_payload[p], 'u':message_payload['u'],'t':message_payload['t']}}
        apns_string = json.dumps(apns_dict,ensure_ascii=False)
        message = {'default':message_payload['message'],'GCM':apns_string}
        messageJSON = json.dumps(message,ensure_ascii=False)
        
    try:
        message = PushMessage(badge_count=1, context='url_alert', context_id='none',has_new_content=True, message=messageJSON, sound="default")
    except Exception as e:
        return 0
    try:
        device = Device.objects.get(device_id=device_id)
        device.send(message)
    except Exception as e:
        return 0
        
