from django.db import models

from common.utils import slugify


class CreateGetFromDataManagerMixin(object):
    def create_or_get_from_data(self, data, key='text'):
        '''
        This function either creates or fetches objects from database
        based on Id or slug created using text attribute
        '''
        id = data.get('id')
        text = data.get(key)
        instance = None
        if id:
            try:
                instance = self.get(id=id)
            except models.ObjectDoesNotExist as e:
                instance = None
        elif text:
            slug = slugify(text)
            try:
                instance = self.get(slug=slug)
            except models.ObjectDoesNotExist as e:
                instance = self.create(**{key: text.title(), 'slug': slug})
        return instance
