import datetime
import urllib
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


class TimeBasedPaginator:

    def __init__(self, query_set, request, time_field='created_on'):
        self.query_set = query_set
        self.time_field = time_field
        self.request = request

        self.init()

    def init(self):
        self.after = self.request.query_params.get('after', None)
        self.before = self.request.query_params.get('before', None)
        self.item_count = int(self.request.query_params.get('item_count', 30))
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
        next_url = self.request.build_absolute_uri(
            reverse('discussions-list')) + '?' + urllib.parse.urlencode(next_url_params)

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
            prev_url = self.request.build_absolute_uri(
                reverse('discussions-list')) + '?' + urllib.parse.urlencode(prev_url_params)
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
