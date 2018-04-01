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

    def get_absolute_url(self):
        if self.storage == self.STORAGE_S3:
            return self.get_absolute_url_s3()

        return self.filename

    def get_absolute_url_s3(self):
        custom_domain = settings.AWS_S3_CUSTOM_DOMAIN

        if custom_domain:
            return "https://%s/%s" % (custom_domain, self.filename)

        bucket_name= settings.AWS_STORAGE_BUCKET_NAME
        if bucket_name:
            return "https://%s.s3.amazonaws.com/%s" % (bucket_name, self.filename)

        return self.filename

    @classmethod
    def create(cls, the_file, filename, file_md5sum=None):
        s3 = boto3.client('s3')

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        try:
            md5sum = s3.head_object(Bucket=bucket_name, Key=filename)['ETag'][1:-1]
            if file_md5sum is None:
                file_md5sum = self._get_hash(the_file)
            if md5sum != file_md5sum:
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


    @staticmethod
    def _get_hash(the_file):
        m = hashlib.md5()
        while True:
            chunk = the_file.read(2**20)
            if chunk == b"":
                break
            m.update(chunk)
        the_file.seek(0)

        return m.hexdigest()
        

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
