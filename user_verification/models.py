from django.db import models


class UserVerification(models.Model):

    id = models.UUIDField(primary_key=True)
    visual_check_image = models.CharField(max_length=255)
    profile_created = models.BooleanField(default=False)
    probability = models.FloatField()
    match = models.BooleanField()
    match_id = models.UUIDField(null=True)
    audio_captcha_sentence = models.CharField(default=None, max_length=100, null=True)
    audio_captcha_result = models.NullBooleanField(default=None, null=True)
    user_verification_video = models.CharField(max_length=255, null=True, default=None)
