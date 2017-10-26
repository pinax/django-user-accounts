from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from account.models import EmailAddress
from account.utils import get_user_lookup_kwargs


class UsernameAuthenticationBackend(ModelBackend):

    def authenticate(self, **credentials):
        User = get_user_model()
        try:
            lookup_kwargs = get_user_lookup_kwargs({
                "{username}__iexact": credentials["username"]
            })
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
