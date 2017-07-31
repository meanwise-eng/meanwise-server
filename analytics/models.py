from django.db import models


class SeenPostBatch(models.Model):
    url = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return str(self.url)


class SeenPost(models.Model):
    batch = models.ForeignKey(SeenPostBatch,
                              related_name='posts',
                              on_delete=models.CASCADE,
                              db_index=True)
    post_id = models.IntegerField(blank=False)
    user_id = models.IntegerField(null=False, blank=False)
    poster = models.IntegerField(null=False, blank=False)
    page_no = models.IntegerField(null=False, blank=False)
    datetime = models.DateTimeField(auto_now_add=False)
    no_in_sequence = models.IntegerField(null=False, blank=False)
    is_expanded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.post_id)
