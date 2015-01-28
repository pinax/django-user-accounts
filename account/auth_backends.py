from __future__ import unicode_literals

from django.db.models import Q

from django.contrib.auth.backends import ModelBackend

from account.compat import get_user_model, get_user_lookup_kwargs
from account.models import EmailAddress


class UsernameAuthenticationBackend(ModelBackend):

    def authenticate(self, username, password):
        User = get_user_model()
        lookup_kwargs = get_user_lookup_kwargs({
            "{username}__iexact": username,
        })
        try:
            user = User.objects.get(**lookup_kwargs)
        except (User.DoesNotExist, KeyError):
            return None
        else:
            try:
                if user.check_password(password):
                    return user
            except KeyError:
                return None


class EmailAuthenticationBackend(ModelBackend):

    def authenticate(self, username, password):
        qs = EmailAddress.objects.filter(Q(primary=True) | Q(verified=True))
        try:
            email_address = qs.get(email__iexact=username)
        except (EmailAddress.DoesNotExist, KeyError):
            return None
        else:
            user = email_address.user
            try:
                if user.check_password(password):
                    return user
            except KeyError:
                return None
