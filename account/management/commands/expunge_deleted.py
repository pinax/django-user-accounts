from __future__ import print_function
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from account.models import AccountDeletion


class Command(BaseCommand):

    help = "Expunge accounts deleted more than 48 hours ago."

    def handle(self, *args, **options):
        count = AccountDeletion.expunge()
        print("{0} expunged.".format(count))
