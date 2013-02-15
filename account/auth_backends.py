from __future__ import unicode_literals

import re

from django.db.models import Q

from django.contrib.auth.backends import ModelBackend

from account.compat import get_user_model, get_user_lookup_kwargs
from account.models import EmailAddress


email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*" # dot-atom
    # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
    r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)' # domain
    r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE) # literal form, ipv4 address (SMTP 4.1.3)


class UsernameAuthenticationBackend(ModelBackend):

    def authenticate(self, **credentials):
        User = get_user_model()
        lookup_kwargs = get_user_lookup_kwargs({
            "{username}__iexact": credentials["username"]
        })
        try:
            user = User.objects.get(**lookup_kwargs)
        except (User.DoesNotExist, KeyError):
            return None
        else:
            try:
                if user.check_password(credentials["password"]):
                    return user
            except KeyError:
               return None 

class EmailAuthenticationBackend(ModelBackend):

    def authenticate(self, **credentials):
        qs = EmailAddress.objects.filter(Q(primary=True) | Q(verified=True))
        try:
            email_address = qs.get(email__iexact=credentials["username"])
        except (EmailAddress.DoesNotExist, KeyError):
            return None
        else:
            user = email_address.user
            try:
                if user.check_password(credentials["password"]):
                    return user
            except KeyError:
                return None

class HybridAuthenticationBackend(ModelBackend):
    """User can login via email OR username"""
    def authenticate(self, **credentials):
        User = get_user_model()
        if email_re.search(credentials["username"]):
            qs = EmailAddress.objects.filter(Q(primary=True) | Q(verified=True))
            try: email_address = qs.get(email__iexact=credentials["username"])
            except (EmailAddress.DoesNotExist, KeyError): return None
            else: user = email_address.user
        else:
            lookup_kwargs = get_user_lookup_kwargs({
                "{username}__iexact": credentials["username"]
            })
            try: user = User.objects.get(**lookup_kwargs)
            except (User.DoesNotExist, KeyError): return None
        try:
            if user.check_password(credentials["password"]):
                return user
        except KeyError:
            return None
