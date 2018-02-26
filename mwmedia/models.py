from django.db import models

class MediaFile(models.Model):

    STORAGE_S3 = 's3'

    filename = models.CharField(max_length=255, primary_key=True)
    storage = models.CharField(max_length=20)
    orphan = models.BooleanField(default=True)
    uploaded_time = models.DateTimeField(auto_now_add=True)

    @classmethod
    def claim(cls, filename):
        try:
            f = MediaFile.objects.get(filename=filename)
        except MediaFile.DoesNotExist:
            raise Exception("File '%s' doesn't exist." % filename)

        f.orphan = False
        f.save()
