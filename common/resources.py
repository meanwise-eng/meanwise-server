from restless.dj import DjangoResource


class DefaultResource(DjangoResource):
    '''
    This is the default resource class that will be used throughout the app.
    This class will providing methods for returning response for both authenticated user
    and un authenticated user.
    '''
    def is_authenticated(self):
        return True  # Allow every request

    def serialize(self, method, endpoint, data):
        """
        This method has been overriden because for list API calls restless by
        default calls preparer for each instance. But our DefaultPreparer
        handles both multiple and single objects.
        """
        if data is None:
            return ''

        # Check for a ``Data``-like object. We should assume ``True`` (all
        # data gets prepared) unless it's explicitly marked as not.
        if not getattr(data, 'should_prepare', True):
            prepped_data = data.value
        else:
            prepped_data = self.prepare(data)

        return self.serializer.serialize(prepped_data)
