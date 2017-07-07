from django.db import models
from enum_field import Enum, EnumField

class Version(models.Model):

	PLATFORMS = Enum(
		('ios', 'iOS'),
		('android', 'Android'),
	)
	PLATFORMS.set_ui_labels({
		PLATFORMS.iOS: 'iOS',
		PLATFORMS.Android: 'Android',
	})

	STATUS_DRAFT = 0
	STATUS_PUBLISHED = 1
	STATUS_INACTIVE = -1

	STATUSES = (
		(-1, 'Inactive'),
		(0, 'Draft'),
		(1, 'Published'),
	)

	version_string = models.CharField(null=False, max_length=10)
	version_sort = models.CharField(null=False, max_length=10)
	status = models.IntegerField(default=STATUS_DRAFT, choices=STATUSES)
	platform = EnumField(PLATFORMS)

	def publish(self):
		if self.status != self.STATUS_DRAFT:
			raise Exception("You can only publish draft versions.")
		self.status = self.STATUS_PUBLISHED

	def deactivate(self):
		if self.status != self.STATUS_PUBLISHED:
			raise Exception("You can only deactivate published versions.")
		self.status = self.STATUS_INACTIVE

	def save(self):
		if self.version_string:
			vParts = self.version_string.split('.')
			vParts = map(lambda x: x.zfill(3), vParts)
			self.version_sort = ''.join(vParts)

		super().save()