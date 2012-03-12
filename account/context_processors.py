from account.conf import settings


def account(request):
    ctx = {
        "open_signup": settings.ACCOUNT_OPEN_SIGNUP,
    }
    return ctx
