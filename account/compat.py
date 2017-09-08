import django

try:
    from django.core.urlresolvers import resolve, reverse, NoReverseMatch
except ImportError:
    from django.urls import resolve, reverse, NoReverseMatch  # noqa

if django.VERSION >= (1, 9, 0):
    from django.contrib.auth.password_validation import validate_password
else:
    def validate_password(password, user=None, password_validators=None):
        pass


def is_authenticated(user):
    if django.VERSION >= (1, 10):
        return user.is_authenticated
    else:
        return user.is_authenticated()
