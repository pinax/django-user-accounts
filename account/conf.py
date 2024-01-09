import importlib

from django.conf import settings  # noqa
from django.core.exceptions import ImproperlyConfigured

from account.languages import LANGUAGES
from account.timezones import TIMEZONES
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
    LOGOUT_URL = "account_logout"
    SIGNUP_REDIRECT_URL = "/"
    LOGIN_REDIRECT_URL = "/"
    LOGOUT_REDIRECT_URL = "/"
    PASSWORD_CHANGE_REDIRECT_URL = "account_password"
    PASSWORD_RESET_REDIRECT_URL = "account_login"
    PASSWORD_RESET_TOKEN_URL = "account_password_reset_token"
    PASSWORD_EXPIRY = 0
    PASSWORD_USE_HISTORY = False
    ACCOUNT_APPROVAL_REQUIRED = False
    PASSWORD_STRIP = True
    REMEMBER_ME_EXPIRY = 60 * 60 * 24 * 365 * 10
    USER_DISPLAY = lambda user: user.username  # noqa
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
    DEFAULT_HTTP_PROTOCOL = "https"
    HOOKSET = "account.hooks.AccountDefaultHookSet"
    TIMEZONES = TIMEZONES
    LANGUAGES = LANGUAGES

    @staticmethod
    def configure_hookset(value):
        return load_path_attr(value)()
