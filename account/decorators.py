import functools

from django.contrib.auth import REDIRECT_FIELD_NAME

from account.utils import handle_redirect_to_login


def login_required(func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log in page if necessary.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            return handle_redirect_to_login(
                request,
                redirect_field_name=redirect_field_name,
                login_url=login_url
            )
        return _wrapped_view
    if func:
        return decorator(func)
    return decorator
