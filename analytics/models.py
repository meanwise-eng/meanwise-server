from django.db import models

class SeenPostBatch(models.Model):
    url = models.URLField(max_length=200)
    datetime = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return str(self.url)


class SeenPost(models.Model):
    url = models.ForeignKey(SeenPostBatch,
                            related_name='posts')
    post_id = models.IntegerField(blank=False)
    user_id = models.IntegerField(null=False, blank=False)
    page_no = models.IntegerField(null=False, blank=False)
    datetime = models.DateTimeField(auto_now=True)
    is_expanded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.post_id)
