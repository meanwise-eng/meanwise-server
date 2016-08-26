import logging

from django.core.serializers.json import DjangoJSONEncoder

from rest_framework.response import Response

from .utils import format_error_response

logger = logging.getLogger('squelo_backend')


class FormErrorJsonResponse(Response):
    def __init__(self, errors, status=400, **kwargs):
        messages = []
        for key in errors:
            messages += errors[key]
        messages = messages[:2]
        data = {'message': key.title() +': ' + ' And '.join(messages)}
        logger.error('%s' % str(data))
        super(FormErrorJsonResponse, self).__init__(data, status=status, **kwargs)


class JsonErrorResponse(Response):
    def __init__(self, message, status=400, **kwargs):
        if isinstance(message, dict):
            message = format_error_response(message)
        data = {'message': unicode(message)}
        logger.error('%s' % str(data))
        super(JsonErrorResponse, self).__init__(data, status=status, **kwargs)


class JsonResponse(Response):
    def __init__(self, data, message='', error_message='', encoder=DjangoJSONEncoder, safe=True, **kwargs):
        response = {}
        if data: response['data'] = data
        if message: response['message'] = unicode(message)
        if error_message: response['error'] = {'message': error_message}
        super(JsonResponse, self).__init__(response, **kwargs)
