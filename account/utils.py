import hashlib
import importlib
import random
import urlparse

from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect, QueryDict

from account.conf import settings


def default_redirect(request, fallback_url, **kwargs):
    redirect_field_name = kwargs.get("redirect_field_name", "next")
    next = request.REQUEST.get(redirect_field_name)
    if not next:
        # try the session if available
        if hasattr(request, "session"):
            session_key_value = kwargs.get("session_key_value", "redirect_to")
            next = request.session.get(session_key_value)
    if next:
        netloc = urlparse.urlparse(next)[1]
        redirect_to = next
        # security check -- don't allow redirection to a different host
        if netloc and netloc != request.get_host():
            redirect_to = fallback_url
    else:
        redirect_to = fallback_url
    return redirect_to


def user_display(user):
    return settings.ACCOUNT_USER_DISPLAY(user)


def random_token(extra=None, hash_func=hashlib.sha256):
    if extra is None:
        extra = []
    bits = extra + [str(random.SystemRandom().getrandbits(512))]
    return hash_func("".join(bits)).hexdigest()


def handle_redirect_to_login(request, **kwargs):
    login_url = kwargs.get("login_url")
    redirect_field_name = kwargs.get("redirect_field_name")
    next_url = kwargs.get("next_url")
    if login_url is None:
        login_url = settings.ACCOUNT_LOGIN_URL
    if next_url is None:
        next_url = request.get_full_path()
    try:
        login_url = urlresolvers.reverse(login_url)
    except urlresolvers.NoReverseMatch:
        if callable(login_url):
            raise
        if "/" not in login_url and "." not in login_url:
            raise
    url_bits = list(urlparse.urlparse(login_url))
    if redirect_field_name:
        querystring = QueryDict(url_bits[4], mutable=True)
        querystring[redirect_field_name] = next_url
        url_bits[4] = querystring.urlencode(safe="/")
    return HttpResponseRedirect(urlparse.urlunparse(url_bits))


def load_path_attr(path):
    i = path.rfind(".")
    module, attr = path[:i], path[i+1:]
    try:
        mod = importlib.import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured("Error importing %s: '%s'" % (module, e))
    try:
        attr = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured("Module '%s' does not define a '%s'" % (module, attr))
    return attr
