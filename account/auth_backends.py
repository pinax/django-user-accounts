from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from account.models import EmailAddress
from account.utils import get_user_lookup_kwargs

User = get_user_model()


class AccountModelBackend(ModelBackend):
    """
    This authentication backend ensures that the account is always selected
    on any query with the user, so we don't issue extra unnecessary queries
    """

    def get_user(self, user_id):
        """Get the user and select account at the same time"""
        user = User._default_manager.filter(pk=user_id).select_related("account").first()
        if not user:
            return None
        return user if self.user_can_authenticate(user) else None


class UsernameAuthenticationBackend(AccountModelBackend):
    """Username authentication"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate the user based on user"""
        if username is None or password is None:
            return None

        try:
            lookup_kwargs = get_user_lookup_kwargs({
                "{username}__iexact": username
            })
            user = User.objects.get(**lookup_kwargs)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user


class EmailAuthenticationBackend(AccountModelBackend):
    """Email authentication"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate the user based email"""
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
