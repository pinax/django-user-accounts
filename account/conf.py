import importlib

from django.apps import apps as django_apps
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


def get_email_model():
    """
    Return the Email model that is active in this project.
    This should either be the user model, or the email model provided
    in the project
    """
    try:
        return django_apps.get_model(settings.ACCOUNT_EMAIL_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("ACCOUNT_EMAIL_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "ACCOUNT_EMAIL_MODEL refers to model '%s' that has not been installed" % settings.ACCOUNT_EMAIL_MODEL
        )


def user_as_email():
    return settings.ACCOUNT_EMAIL_MODEL == settings.AUTH_USER_MODEL


class AccountAppConf(AppConf):
    # TODO can we make a check that it's easier the user model or this model?
    EMAIL_MODEL = "account.EmailAddress"
    OPEN_SIGNUP = True
    LOGIN_URL = "account_login"
    LOGOUT_URL = "account_logout"
    SIGNUP_REDIRECT_URL = "/"
    LOGIN_REDIRECT_URL = "/"
    LOGOUT_REDIRECT_URL = "/"
    PASSWORD_CHANGE_REDIRECT_URL = "account_password"
    PASSWORD_RESET_REDIRECT_URL = "account_login"
    PASSWORD_EXPIRY = 0
    PASSWORD_USE_HISTORY = False
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
    HOOKSET = "account.hooks.AccountDefaultHookSet"
    TIMEZONES = TIMEZONES
    LANGUAGES = LANGUAGES

    def configure_hookset(self, value):
        return load_path_attr(value)()
