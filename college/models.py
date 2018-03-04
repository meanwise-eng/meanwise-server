from django.db import models
import uuid

from django.contrib.auth.models import User


class College(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=1000)
    logo = models.ImageField(upload_to='college_logos')
    logo_thumbnail = models.ImageField(upload_to='college_logo_thumbnails', blank=True, null=True)
    profile_color = models.CharField(max_length=7, default='#000000')
    compact_display_image = models.ImageField(upload_to='college_compact_image')

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FeaturedStudent(models.Model):

    student = models.ForeignKey(User)
    college = models.ForeignKey(College, related_name='featured_students')

    def __str__(self):
        return "{} in {}".format(self.student.username, self.college.name)
