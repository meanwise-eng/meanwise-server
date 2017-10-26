import datetime
import urllib
import re
import logging
from urlobject import URLObject

from django.conf import settings
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_objects_paginated(objects, page, page_size=settings.REST_FRAMEWORK['PAGE_SIZE']):
    """
    Generic pagination for objects

    """
    if not page_size:
        page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
    paginator = Paginator(objects, page_size)
    has_next_page = False
    num_pages = paginator.num_pages
    try:
        objects = paginator.page(page)
        has_next_page = objects.has_next()
    except PageNotAnInteger:
        objects = paginator.page(1)
        has_next_page = objects.has_next()
    except EmptyPage:
        objects = []
        # paginator.page(paginator.num_pages)
    return objects, has_next_page, num_pages


def get_objects_paginated_offset(objects, offset=0, limit=settings.REST_FRAMEWORK['PAGE_SIZE']):
    """
    Generic pagination for objects

    """
    paginator = Paginator(objects, limit)
    page = int((int(offset) - 1) / int(limit)) + 1
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return objects


def build_absolute_uri(uri, params=None):
    logger = logging.getLogger('meanwise_backend.%s' % __name__)

    base_uri = settings.BASE_URI
    base_api_path = '/api/v4/'
    regex = re.compile(base_api_path)

    logger.debug("Base URI: %s" % base_uri)
    logger.debug("New URI: %s" % uri)

    b_uri_p = urllib.parse.urlparse(base_uri)
    n_uri_p = urllib.parse.urlparse(uri)
    new_path = regex.sub(b_uri_p.path, n_uri_p.path)

    logger.debug("New Path: %s" % new_path)

    new_uri = b_uri_p[0:2] + (new_path,) + n_uri_p[3:]

    url = URLObject(urllib.parse.urlunparse(new_uri))
    if params:
        url = url.with_query(url.query.set_params(params))

    logger.debug("New URI: %s" % (url,))
    return str(url)


class TimeBasedPaginator:

    def __init__(self, query_set, request, time_field='created_on'):
        self.query_set = query_set
        self.time_field = time_field
        self.request = request

        self.init()

    def init(self):
        self.after = self.request.query_params.get('after', None)
        self.before = self.request.query_params.get('before', None)
        self.item_count = int(self.request.query_params.get(
            'item_count',
            settings.REST_FRAMEWORK['PAGE_SIZE']
        ))
        self.section = int(self.request.query_params.get('section', 1))
        if self.after:
            self.after = datetime.datetime.fromtimestamp(float(self.after) / 1000)
        if self.before:
            self.before = datetime.datetime.fromtimestamp(float(self.before) / 1000)
        if self.item_count > 100:
            raise Exception("item_count greater than 100 is not allowed.")

        now = datetime.datetime.now()

        q = self.query_set
        if self.after:
            kwargs = {}
            kwargs['%s__gt' % self.time_field] = self.after
            q = q.filter(**kwargs)
        if self.before:
            kwargs = {}
            kwargs['%s__lte' % self.time_field] = self.before
            q = q.filter(**kwargs)

        total = q.count()

        query_params = dict(self.request.query_params)

        after_date = self.before if self.before else now

        new_params = {}
        try:
            new_params['after'] = str(int(after_date.timestamp() * 1000))
        except Exception:
            pass
        next_url_params = {k: p[0] for k, p in query_params.copy().items()}
        if 'before' in next_url_params:
            del next_url_params['before']
        next_url_params.update(new_params)
        next_url = build_absolute_uri(
            self.request.path_info) + '?' + urllib.parse.urlencode(next_url_params)

        new_params = {}
        if self.before:
            before_date = self.before
            new_params['section'] = self.section + 1
        else:
            before_date = now
            new_params['section'] = 2

        if before_date and self.section * self.item_count < total:
            try:
                new_params['before'] = str(int(before_date.timestamp() * 1000))
            except Exception:
                pass

            prev_url_params = {k: p[0] for k, p in query_params.copy().items()}
            if 'after' in prev_url_params:
                del prev_url_params['after']
            prev_url_params.update(new_params)
            prev_url = build_absolute_uri(
                self.request.path_info) + '?' + urllib.parse.urlencode(prev_url_params)
        else:
            prev_url = None

        self.next_url = next_url
        self.prev_url = prev_url
        self.total = total
        self.total_pages = int(self.total / self.item_count) + 1
        offset = (self.section - 1) * self.item_count
        self.paginated_query_set = q[offset:offset + self.item_count]

    def page(self):
        return self.paginated_query_set


class NormalPaginator:

    def __init__(self, query_set, request):
        item_count = request.query_params.get('item_count', settings.REST_FRAMEWORK['PAGE_SIZE'])
        page = int(request.query_params.get('page', 1))
        total = query_set.count()
        self.request = request

        paginator = Paginator(query_set, item_count)
        has_next_page = False

        try:
            objects = paginator.page(self.page)
            has_next_page = objects.has_next()
        except PageNotAnInteger:
            objects = paginator.page(1)
            has_next_page = objects.has_next()
        except EmptyPage:
            objects = []
        self.objects = objects

        next_url = None

        if has_next_page:
            new_params = {'page': (page + 1)}
            prev_url = self.get_new_url_from_params(new_params, request)
        else:
            prev_url = None

        self.total_pages = paginator.num_pages
        self.total = total
        self.next_url = next_url
        self.prev_url = prev_url

    def page(self):
        return self.objects

    def get_new_url_from_params(self, new_params, request):
        query_params = dict(self.request.query_params)
        prev_url_params = {k: p[0] for k, p in query_params.copy().items()}
        prev_url_params.update(new_params)
        return build_absolute_uri(
            request.path_info) + '?' + urllib.parse.urlencode(prev_url_params)
