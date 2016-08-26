import os
import uuid

from django.conf import settings
from django.utils.crypto import get_random_string


def handle_workitem_image_upload(f, upload_to='workitem_images'):
    dir_name = os.path.join(settings.MEDIA_ROOT, upload_to)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    ext = os.path.splitext(f.name)[1]
    file_name = '%s%s' % (uuid.uuid4(), ext)
    file_path = os.path.join(dir_name, file_name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return '%s/%s' % (upload_to, file_name)
