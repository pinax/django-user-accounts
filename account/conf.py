from django.conf import settings

from appconf import AppConf


class AccountAppConf(AppConf):
    
    SIGNUP_REDIRECT_URL = "/"
    LOGIN_REDIRECT_URL = "/"
    LOGOUT_REDIRECT_URL = "/"
    EMAIL_VERIFICATION = False
    USER_DISPLAY = lambda user: user.username
    EMAIL_CONFIRMATION_DAYS = 3
