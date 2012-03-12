import hashlib
import random
import urlparse

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
