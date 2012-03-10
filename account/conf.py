from django.conf import settings

from appconf import AppConf


class AccountAppConf(AppConf):
    
    LOGIN_REDIRECT_URL = "/"
    LOGOUT_REDIRECT_URL = "/"
    SIGNUP_DISABLED = False
    LOGIN_DISABLED = False
