from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import resolve, reverse
from django.shortcuts import redirect
from django.utils import translation, timezone
from django.utils.cache import patch_vary_headers
from django.utils.translation import ugettext_lazy as _

from account import signals
from account.conf import settings
from account.models import Account
from account.utils import check_password_expired


class LocaleMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context depending on the user's account. This allows pages
    to be dynamically translated to the language the user desires
    (if the language is available, of course).
    """

    def get_language_for_user(self, request):
        if request.user.is_authenticated():
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


class TimezoneMiddleware(object):
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


class ExpiredPasswordMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated() and not request.user.is_staff:
            url_name = resolve(request.path).url_name
            # All users must be allowed to access "change password" url.
            if url_name not in [
                    settings.ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL,
                    ]:
                if check_password_expired(request.user):
                    signals.password_expired.send(sender=self, user=request.user)
                    messages.add_message(
                        request,
                        messages.WARNING,
                        _("Your password has expired. Please save a new password.")
                    )
                    redirect_url = "{}?next={}".format(reverse(settings.ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL), url_name)

                    return redirect(redirect_url)
