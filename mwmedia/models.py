import boto3
import botocore
import hashlib

from django.db import models
from django.conf import settings


class MediaFile(models.Model):

    STORAGE_S3 = 's3'

    filename = models.CharField(max_length=255, primary_key=True)
    storage = models.CharField(max_length=20)
    orphan = models.BooleanField(default=True)
    uploaded_time = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, the_file, filename):
        s3 = boto3.client('s3')

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        try:
            md5sum = s3.head_object(Bucket=bucket_name, Key=filename)['ETag'][1:-1]
            m = hashlib.md5()
            while True:
                chunk = the_file.read(2**20)
                if chunk == b"":
                    break
                m.update(chunk)
            the_file.seek(0)
            if md5sum != m.hexdigest():
                raise Exception("The two files are not the same. You cannot replace existing files.")
            else:
                try:
                    media = MediaFile.objects.get(filename=filename)
                except MediaFile.DoesNotExist:
                    media = MediaFile(filename=filename, storage=MediaFile.STORAGE_S3)
                    media.save()

                raise MediaFile.FileAlreadyExists("The file '%s' already exists in storage")
        except botocore.exceptions.ClientError:
            pass

        try:
            response = s3.put_object(
                ACL='public-read',
                Bucket=bucket_name,
                Body=the_file,
                Key=filename,
            )
        except Exception:
            raise MediaFile.FailedToSave("The file '%s' failed to save.")

        media = MediaFile(filename=filename, storage=MediaFile.STORAGE_S3)
        media.save()

        return media
        

    @classmethod
    def claim(cls, filename):
        try:
            f = MediaFile.objects.get(filename=filename)
        except MediaFile.DoesNotExist:
            raise MediaFile.MediaFileDoesNotExist("MediaFile '%s' doesn't exist." % filename)

        if f.orphan == False:
            raise MediaFile.MediaFileIsAlreadyClaimed("MediaFile '%s' is already claimed." % filename)

        f.orphan = False
        f.save()


    class MediaFileException(Exception):
        pass


    class FailedToSave(MediaFileException):
        pass


    class MediaFileDoesNotExist(MediaFileException):
        pass


    class FileAlreadyExists(MediaFileException):
        pass
    
    
    class MediaFileIsAlreadyClaimed(MediaFileException):
        pass
