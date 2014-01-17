try:
    from django.contrib.auth import get_user_model as auth_get_user_model
except ImportError:
    auth_get_user_model = None
    from django.contrib.auth.models import User

from account.conf import settings


AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


def get_user_model(*args, **kwargs):
    if auth_get_user_model is not None:
        return auth_get_user_model(*args, **kwargs)
    else:
        return User


def get_user_lookup_kwargs(kwargs):
    result = {}
    username_field = getattr(get_user_model(), "USERNAME_FIELD", "username")
    for key, value in kwargs.items():
        result[key.format(username=username_field)] = value
    return result
