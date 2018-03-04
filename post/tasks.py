from __future__ import absolute_import, unicode_literals

import os
import logging
import tempfile

from moviepy.editor import VideoFileClip

from django.core.files import File

from meanwise_backend.celery import app

import post.models

logger = logging.getLogger('meanwise_backend.%s' % __name__)

@app.task
def generate_video_thumbnail(post_id):
    logger.info("Post ID: %s" % post_id)
    p = post.models.Post.objects.get(id=post_id)

    filename = os.path.splitext(os.path.basename(p.video.name))[0]
    ext = os.path.splitext(os.path.basename(p.video.name))[-1]

    clip = VideoFileClip(p.video.url)
    with tempfile.NamedTemporaryFile('r+b', suffix='.jpg') as tmp_thumb_file:
        clip.save_frame(tmp_thumb_file.name , t=1.00)
        _file = File(tmp_thumb_file)
        p.video_thumbnail.save((filename + ".jpg"), _file, save=True)

    p.resolution = {
        'height': p.video_thumbnail.height,
        'width': p.video_thumbnail.width
    }

    p.save()