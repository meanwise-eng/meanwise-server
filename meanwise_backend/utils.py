from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
    	data = response.data
    	response_data = {'status': 'failed', 'error': data, 'results': ''}
    	response.data = response_data

    return response