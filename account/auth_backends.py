from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from account.models import EmailAddress
from account.utils import get_user_lookup_kwargs


class UsernameAuthenticationBackend(ModelBackend):
    """
    When the email model is the User, this authentication works just fine
    for authenticating the user through email
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        User = get_user_model()
        try:
            lookup_kwargs = get_user_lookup_kwargs({
                "{username}__iexact": username
            })
            user = User.objects.get(**lookup_kwargs)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user


class EmailAuthenticationBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # TODO, remove primary true, username shouldn't be necessary either?
        # should use email model. This probably doesn't need to be modified
        qs = EmailAddress.objects.filter(Q(primary=True) | Q(verified=True))

        if username is None or password is None:
            return None

        try:
            email_address = qs.get(email__iexact=username)
        except EmailAddress.DoesNotExist:
            return None

        user = email_address.user
        if user.check_password(password):
            return user
