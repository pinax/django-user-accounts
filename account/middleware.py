from __future__ import unicode_literals

try:
    from urllib.parse import urlparse, urlunparse
except ImportError:  # python 2
    from urlparse import urlparse, urlunparse

import django

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect, QueryDict
from django.utils import translation, timezone
from django.utils.cache import patch_vary_headers
from django.utils.translation import ugettext_lazy as _

from account import signals
from account.compat import resolve, reverse, is_authenticated
from account.conf import settings
from account.models import Account
from account.utils import check_password_expired


if django.VERSION >= (1, 10):
    from django.utils.deprecation import MiddlewareMixin as BaseMiddleware
else:
    BaseMiddleware = object


class LocaleMiddleware(BaseMiddleware):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context depending on the user's account. This allows pages
    to be dynamically translated to the language the user desires
    (if the language is available, of course).
    """

    def get_language_for_user(self, request):
        if is_authenticated(request.user):
            try:
                account = Account.objects.get(user=request.user)
                return account.language
            except Account.DoesNotExist:
                pass
        return translation.get_language_from_request(request)

    def process_request(self, request):
        translation.activate(self.get_language_for_user(request))
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        patch_vary_headers(response, ("Accept-Language",))
        response["Content-Language"] = translation.get_language()
        translation.deactivate()
        return response


class TimezoneMiddleware(BaseMiddleware):
    """
    This middleware sets the timezone used to display dates in
    templates to the user's timezone.
    """

    def process_request(self, request):
        try:
            account = getattr(request.user, "account", None)
        except Account.DoesNotExist:
            pass
        else:
            if account:
                tz = settings.TIME_ZONE if not account.timezone else account.timezone
                timezone.activate(tz)


class ExpiredPasswordMiddleware(BaseMiddleware):

    def process_request(self, request):
        if is_authenticated(request.user) and not request.user.is_staff:
            next_url = resolve(request.path).url_name
            # Authenticated users must be allowed to access
            # "change password" page and "log out" page.
            # even if password is expired.
            if next_url not in [settings.ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL,
                                settings.ACCOUNT_LOGOUT_URL,
                                ]:
                if check_password_expired(request.user):
                    signals.password_expired.send(sender=self, user=request.user)
                    messages.add_message(
                        request,
                        messages.WARNING,
                        _("Your password has expired. Please save a new password.")
                    )
                    redirect_field_name = REDIRECT_FIELD_NAME

                    change_password_url = reverse(settings.ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL)
                    url_bits = list(urlparse(change_password_url))
                    querystring = QueryDict(url_bits[4], mutable=True)
                    querystring[redirect_field_name] = next_url
                    url_bits[4] = querystring.urlencode(safe="/")

                    return HttpResponseRedirect(urlunparse(url_bits))
