from account.conf import settings

from account.models import Account


def account(request):
    ctx = {
        "account": Account.for_request(request),
        "ACCOUNT_OPEN_SIGNUP": settings.ACCOUNT_OPEN_SIGNUP,
        "ACCOUNT_CONTACT_EMAIL": settings.ACCOUNT_CONTACT_EMAIL,
    }
    return ctx
