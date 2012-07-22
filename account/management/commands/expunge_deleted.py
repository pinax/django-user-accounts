from django.core.management.base import BaseCommand

from account.models import expunge_deleted


class Command(BaseCommand):
    help = "Expunge accounts deleted more than 48 hours ago."
    
    def handle(self, *args, **options):
        count = expunge_deleted()
        print "%d expunged." % count
