import datetime

from time import sleep

from django.core.management.base import BaseCommand

import elasticsearch

from credits.models import Credits


class Command(BaseCommand):
    help = 'Recalculate the user topics'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for credit in Credits.objects.all():
            if credit.skill == credit.skill.upper():
                continue

            try:
                uppercase_credit = Credits.objects.get(user_id=credit.user_id, skill=credit.skill.upper())
            except Credits.DoesNotExist:
                credit.skill = credit.skill.upper()
                credit.save()
            else:
                uppercase_credit.credits += credit.credits
                uppercase_credit.save()
                credit.delete()
