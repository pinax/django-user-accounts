from django.urls import resolve, reverse, NoReverseMatch  # noqa


def is_authenticated(user):
    return user.is_authenticated
