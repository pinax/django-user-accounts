from __future__ import unicode_literals

import datetime
import functools
import pytz
try:
    from urllib.parse import urlparse, urlunparse
except ImportError:  # python 2
    from urlparse import urlparse, urlunparse

from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect, QueryDict

from django.contrib.auth import get_user_model

from account.compat import reverse, NoReverseMatch
from account.conf import settings
from .models import PasswordHistory


def get_user_lookup_kwargs(kwargs):
    result = {}
    username_field = getattr(get_user_model(), "USERNAME_FIELD", "username")
    for key, value in kwargs.items():
        result[key.format(username=username_field)] = value
    return result


def default_redirect(request, fallback_url, **kwargs):
    redirect_field_name = kwargs.get("redirect_field_name", "next")
    next_url = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name))
    if not next_url:
        # try the session if available
        if hasattr(request, "session"):
            session_key_value = kwargs.get("session_key_value", "redirect_to")
            if session_key_value in request.session:
                next_url = request.session[session_key_value]
                del request.session[session_key_value]
    is_safe = functools.partial(
        ensure_safe_url,
        allowed_protocols=kwargs.get("allowed_protocols"),
        allowed_host=request.get_host()
    )
    if next_url and is_safe(next_url):
        return next_url
    else:
        try:
            fallback_url = reverse(fallback_url)
        except NoReverseMatch:
            if callable(fallback_url):
                raise
            if "/" not in fallback_url and "." not in fallback_url:
                raise
        # assert the fallback URL is safe to return to caller. if it is
        # determined unsafe then raise an exception as the fallback value comes
        # from the a source the developer choose.
        is_safe(fallback_url, raise_on_fail=True)
        return fallback_url


def user_display(user):
    return settings.ACCOUNT_USER_DISPLAY(user)


def ensure_safe_url(url, allowed_protocols=None, allowed_host=None, raise_on_fail=False):
    if allowed_protocols is None:
        allowed_protocols = ["http", "https"]
    parsed = urlparse(url)
    # perform security checks to ensure no malicious intent
    # (i.e., an XSS attack with a data URL)
    safe = True
    if parsed.scheme and parsed.scheme not in allowed_protocols:
        if raise_on_fail:
            raise SuspiciousOperation("Unsafe redirect to URL with protocol '{0}'".format(parsed.scheme))
        safe = False
    if allowed_host and parsed.netloc and parsed.netloc != allowed_host:
        if raise_on_fail:
            raise SuspiciousOperation("Unsafe redirect to URL not matching host '{0}'".format(allowed_host))
        safe = False
    return safe


def handle_redirect_to_login(request, **kwargs):
    login_url = kwargs.get("login_url")
    redirect_field_name = kwargs.get("redirect_field_name")
    next_url = kwargs.get("next_url")
    if login_url is None:
        login_url = settings.ACCOUNT_LOGIN_URL
    if next_url is None:
        next_url = request.get_full_path()
    try:
        login_url = reverse(login_url)
    except NoReverseMatch:
        if callable(login_url):
            raise
        if "/" not in login_url and "." not in login_url:
            raise
    url_bits = list(urlparse(login_url))
    if redirect_field_name:
        querystring = QueryDict(url_bits[4], mutable=True)
        querystring[redirect_field_name] = next_url
        url_bits[4] = querystring.urlencode(safe="/")
    return HttpResponseRedirect(urlunparse(url_bits))


def get_form_data(form, field_name, default=None):
    if form.prefix:
        key = "-".join([form.prefix, field_name])
    else:
        key = field_name
    return form.data.get(key, default)


def check_password_expired(user):
    """
    Return True if password is expired and system is using
    password expiration, False otherwise.
    """
    if not settings.ACCOUNT_PASSWORD_USE_HISTORY:
        return False

    if hasattr(user, "password_expiry"):
        # user-specific value
        expiry = user.password_expiry.expiry
    else:
        # use global value
        expiry = settings.ACCOUNT_PASSWORD_EXPIRY

    if expiry == 0:  # zero indicates no expiration
        return False

    try:
        # get latest password info
        latest = user.password_history.latest("timestamp")
    except PasswordHistory.DoesNotExist:
        return False

    now = datetime.datetime.now(tz=pytz.UTC)
    expiration = latest.timestamp + datetime.timedelta(seconds=expiry)

    if expiration < now:
        return True
    else:
        return False
