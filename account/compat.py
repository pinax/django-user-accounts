import django

try:
    from django.core.urlresolvers import resolve, reverse, NoReverseMatch
except ImportError:
    from django.urls import resolve, reverse, NoReverseMatch  # noqa


def is_authenticated(user):
    if django.VERSION >= (1, 10):
        return user.is_authenticated
    else:
        return user.is_authenticated()
