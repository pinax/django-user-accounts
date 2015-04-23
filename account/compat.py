import django

from django.db.models.signals import class_prepared
from django.utils import six

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


def receiver(signal, **kwargs):  # noqa
    if django.VERSION < (1, 7, 0):
        unresolved_references = {}

        def _resolve_references(sender, **kwargs):
            opts = sender._meta
            reference = (opts.app_label, opts.object_name)
            try:
                receivers = unresolved_references.pop(reference)
            except KeyError:
                pass
            else:
                for signal, func, kwargs in receivers:
                    kwargs["sender"] = sender
                    signal.connect(func, **kwargs)
        class_prepared.connect(_resolve_references, weak=False)

    def _decorator(func):  # noqa
        if django.VERSION < (1, 7, 0):
            from django.db.models.loading import cache as app_cache
            sender = kwargs.get("sender")
            if isinstance(sender, six.string_types):
                try:
                    app_label, model_name = sender.split(".")
                except ValueError:
                    raise ValueError(
                        "Specified sender must either be a model or a "
                        "model name of the 'app_label.ModelName' form."
                    )
                sender = app_cache.app_models.get(app_label, {}).get(model_name.lower())
                if sender is None:
                    ref = (app_label, model_name)
                    refs = unresolved_references.setdefault(ref, [])
                    refs.append((signal, func, kwargs))
                    return func
                else:
                    kwargs["sender"] = sender
        signal.connect(func, **kwargs)
        return func
    return _decorator
