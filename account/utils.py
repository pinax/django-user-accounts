import urlparse


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
