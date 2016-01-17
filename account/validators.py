from __future__ import unicode_literals

import re

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from account.conf import settings
from account.models import EmailAddress
from account.utils import get_user_lookup_kwargs

alnum_re = re.compile(r"^\w+$")


class Validator():
    @staticmethod
    def clean_username(username):
        if not alnum_re.search(username):
            return _("Usernames can only contain letters, numbers and underscores.")
        User = get_user_model()
        lookup_kwargs = get_user_lookup_kwargs({
            "{username}__iexact": username
        })
        qs = User.objects.filter(**lookup_kwargs)
        if not qs.exists():
            return None
        return _("This username is already taken. Please choose another.")

    @staticmethod
    def clean_email(email):
        qs = EmailAddress.objects.filter(email__iexact=email)
        if not qs.exists() or not settings.ACCOUNT_EMAIL_UNIQUE:
            return None
        return _("A user is registered with this email address.")

    @staticmethod
    def compare_passwords(password, password_confirm):
        if password != password_confirm:
            return _("You must type the same password each time.")

        return None
