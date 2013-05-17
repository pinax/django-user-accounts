# coding=utf8
from __future__ import print_function

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from django.core import urlresolvers
 
from account.models import SignupCode

class Command(BaseCommand):
    args = '<count> <filename> [<expiry_in_days_from_now>]'
    help = 'Generates signup codes and outputs url to file'

    def handle(self, *args, **options):
        site = Site.objects.get_current()
        
        expiry = int(args[2]) if len(args) > 2 else 768
        with open(args[1], mode="w") as fh:
            for i in range(int(args[0])):
                signup = SignupCode.create(max_uses=1, expiry=expiry, check_exists=False)
                fh.write("http://{0}{1}?code={2},".format(site.domain,
                                                          urlresolvers.reverse('account_signup'),
                                                          signup.code))
                signup.save()
