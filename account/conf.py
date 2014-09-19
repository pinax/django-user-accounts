from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import importlib
from django.utils.translation import get_language_info

import pytz

from appconf import AppConf


def load_path_attr(path):
    i = path.rfind(".")
    module, attr = path[:i], path[i + 1:]
    try:
        mod = importlib.import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured("Error importing {0}: '{1}'".format(module, e))
    try:
        attr = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured("Module '{0}' does not define a '{1}'".format(module, attr))
    return attr


class AccountAppConf(AppConf):

    OPEN_SIGNUP = True
    LOGIN_URL = "account_login"
    SIGNUP_REDIRECT_URL = "/"
    LOGIN_REDIRECT_URL = "/"
    LOGOUT_REDIRECT_URL = "/"
    PASSWORD_CHANGE_REDIRECT_URL = "account_password"
    PASSWORD_RESET_REDIRECT_URL = "account_login"
    REMEMBER_ME_EXPIRY = 60 * 60 * 24 * 365 * 10
    USER_DISPLAY = lambda user: user.username
    CREATE_ON_SAVE = True
    EMAIL_UNIQUE = True
    EMAIL_CONFIRMATION_REQUIRED = False
    EMAIL_CONFIRMATION_EMAIL = True
    EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
    EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "account_login"
    EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = None
    EMAIL_CONFIRMATION_URL = "account_confirm_email"
    SETTINGS_REDIRECT_URL = "account_settings"
    NOTIFY_ON_PASSWORD_CHANGE = True
    DELETION_MARK_CALLBACK = "account.callbacks.account_delete_mark"
    DELETION_EXPUNGE_CALLBACK = "account.callbacks.account_delete_expunge"
    DELETION_EXPUNGE_HOURS = 48
    HOOKSET = "account.hooks.AccountDefaultHookSet"
    TIMEZONES = list(zip(pytz.all_timezones, pytz.all_timezones))
    LANGUAGES = [
        (code, get_language_info(code).get("name_local"))
        for code, lang in settings.LANGUAGES
    ]
    USE_AUTH_AUTHENTICATE = False

    def configure_deletion_mark_callback(self, value):
        return load_path_attr(value)

    def configure_deletion_expunge_callback(self, value):
        return load_path_attr(value)

    def configure_hookset(self, value):
        return load_path_attr(value)()
