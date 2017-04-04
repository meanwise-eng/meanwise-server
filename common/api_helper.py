from rest_framework import serializers
from django.conf import settings
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
        #paginator.page(paginator.num_pages)
    return objects, has_next_page, num_pages

def get_objects_paginated_offset(objects, offset=0, limit=settings.REST_FRAMEWORK['PAGE_SIZE']):
    """
    Generic pagination for objects

    """
    paginator = Paginator(objects, limit)
    page = int((int(offset) - 1)/int(limit)) + 1
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return objects