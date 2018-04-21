from __future__ import absolute_import, unicode_literals

import os
import logging
import tempfile
import uuid

from PIL import Image
from io import BytesIO

from moviepy.editor import VideoFileClip

from django.core.files import File

from meanwise_backend.celery import app

import post.models
import mwmedia.models

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

@app.task(bind=True)
def generate_image_thumbnail(self, post_id):
    def do_retry(ex):
        logger.error(ex)
        raise self.retry(ex=ex, countdown=(random.uniform(2, 4) ** self.request.retries))
    logger.info("Generating image thumbnail for %s" % post_id)
    Post = post.models.Post
    try:
        p = Post.objects.get(id=post_id)
    except Post.DoesNotExist as ex:
        logger.info("Post save not yet complete")
        do_retry(ex)

    post_type = p.get_post_type()
    if post_type != Post.TYPE_IMAGE and post_type != Post.TYPE_VIDEO:
        return

    MediaFile = mwmedia.models.MediaFile

    try:
        media = MediaFile.objects.get(filename=p.media_ids[0]['media_id'])
    except MediaFile.DoesNotExist as ex:
        logger.info("Media not ready for generating thumbnail for post %s. Delayed for 1 sec" % post_id)
        do_retry(ex)

    if post_type == Post.TYPE_VIDEO:
        logger.info("Generating video thumbnail")
        filename = os.path.splitext(os.path.basename(p.video.name))[0]
        ext = os.path.splitext(os.path.basename(p.video.name))[-1]
        with tempfile.NamedTemporaryFile('r+b', suffix=ext) as vf:
            for chunk in p.video.chunks():
                vf.write(chunk)
            vf.seek(0)

            clip = VideoFileClip(vf.name)
            with tempfile.NamedTemporaryFile('r+b', suffix='.jpg') as tmp_thumb_file:
                clip.save_frame(tmp_thumb_file.name , t=1.00)
                tmp_thumb_file.seek(0)
                mem_file = BytesIO(tmp_thumb_file.read())
                mem_file.seek(0)

        video_thumb_filename = 'post_video_thumbnails/%s.jpg' % (filename,)
        media = MediaFile.create(mem_file, video_thumb_filename)
        media.orphan = False
        media.save()

        p.video_thumbnail.name = media.filename

        mem_file.seek(0)
        im = Image.open(mem_file)
    else:
        im = Image.open(p.image)

    if not p.resolution:
        p.resolution = {
            'width': im.width,
            'height': im.height,
        }

    if p.thumbnail:
        logger.info("Thumbnail already exists")
        p.save()
        return

    # targetting half of iPhone retina display
    target_width = 750 * 0.5
    scaling_ratio = target_width / im.width
    thumb = im.resize((int(im.width*scaling_ratio), int(im.height*scaling_ratio)),
                      Image.BICUBIC)
    thumb_output = BytesIO()
    thumb.save(thumb_output, format='JPEG', quality=95, optimize=True, progressive=True)
    thumb_output.seek(0)

    filename = 'post_thumbnails/%s.jpg' % (uuid.uuid4(),)
    media = MediaFile.create(thumb_output, filename)
    media.orphan = False
    media.save()

    logger.info("MediaFile '%s' created" % filename)

    p.thumbnail.name = filename
    p.save()

    logger.info("Thumbnail generated for post %s" % post_id)
