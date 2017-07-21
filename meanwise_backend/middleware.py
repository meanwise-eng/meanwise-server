import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.db import connection

class ExtraRequestInfoMiddleware(MiddlewareMixin):

	def process_request(self, request):
		request._start_time = time.time()

	def process_response(self, request, response):
		sqltime = 0.0

		for q in connection.queries:
			sqltime += float(getattr(q, 'time', 0.0))

		if hasattr(request, '_start_time'):
			d = {
				'method': request.method,
				'time': int((time.time() - request._start_time) * 1000),
				'code': response.status_code,
				'url': request.path_info,
				'sql': len(connection.queries),
				'sqltime': sqltime,
				'remote_addr': request.META['REMOTE_ADDR'],
				'bytes': 0,
			}

			extra = {
				'status_code': response.status_code,
				'username': '',
				'user_id': None,
			}
			if hasattr(response, 'content'):
				d['bytes'] = len(response.content)

			if hasattr(request, 'user') and not request.user.is_anonymous():
				extra['username'] = request.user.username
				extra['user_id'] = request.user.id

			msg = '"%(method)s %(url)s" %(code)s %(bytes)d %(time)d (%(sql)dq, %(sqltime).4f) %(remote_addr)s' % d

			logger = logging.getLogger(__name__)
			adapter = logging.LoggerAdapter(logger, extra)
			adapter.info(msg, extra)

		return response