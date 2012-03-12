from account.conf import settings


def account(request):
    ctx = {
        "ACCOUNT_OPEN_SIGNUP": settings.ACCOUNT_OPEN_SIGNUP,
        "ACCOUNT_CONTACT_EMAIL": settings.ACCOUNT_CONTACT_EMAIL,
    }
    return ctx
