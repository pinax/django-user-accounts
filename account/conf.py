from __future__ import unicode_literals

import importlib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import get_language_info

import pytz

from appconf import AppConf

from account.timezones import TIMEZONES
from account.languages import LANGUAGES


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
    LOGOUT_URL = "account_logout"
    SIGNUP_REDIRECT_URL = "/"
    LOGIN_REDIRECT_URL = "/"
    LOGOUT_REDIRECT_URL = "/"
    PASSWORD_CHANGE_REDIRECT_URL = "account_password"
    PASSWORD_RESET_REDIRECT_URL = "account_login"
    INVITE_USER_URL = "account_invite_user"
    ACCOUNT_INVITE_USER_STAFF_ONLY = False
    PASSWORD_EXPIRY = 0
    PASSWORD_USE_HISTORY = False
    PASSWORD_STRIP = True
    REMEMBER_ME_EXPIRY = 60 * 60 * 24 * 365 * 10
    USER_DISPLAY = lambda user: user.username  # flake8: noqa
    CREATE_ON_SAVE = True
    EMAIL_UNIQUE = True
    EMAIL_CONFIRMATION_REQUIRED = False
    EMAIL_CONFIRMATION_EMAIL = True
    EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
    EMAIL_CONFIRMATION_AUTO_LOGIN = False
    EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "account_login"
    EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = None
    EMAIL_CONFIRMATION_URL = "account_confirm_email"
    SETTINGS_REDIRECT_URL = "account_settings"
    NOTIFY_ON_PASSWORD_CHANGE = True
    DELETION_EXPUNGE_HOURS = 48
    HOOKSET = "account.hooks.AccountDefaultHookSet"
    TIMEZONES = TIMEZONES
    LANGUAGES = LANGUAGES

    def configure_hookset(self, value):
        return load_path_attr(value)()
