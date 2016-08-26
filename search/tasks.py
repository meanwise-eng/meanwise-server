from django.core.management import call_command

from celery import task


@task()
def update_search_index(age=3):
    return call_command('update_index', r=True, age=age)
