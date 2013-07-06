from django.db.models import Q

from django.contrib.auth.backends import ModelBackend

from account.models import EmailAddress
from account.utils import get_user_model

UserModel = get_user_model()

class UsernameAuthenticationBackend(ModelBackend):
    
    def authenticate(self, **credentials):
        try:
            user = UserModel.objects.get_by_natural_key(credentials["username"]) # TODO: iexact?
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(credentials["password"]):
                return user


class EmailAuthenticationBackend(ModelBackend):
    
    def authenticate(self, **credentials):
        qs = EmailAddress.objects.filter(Q(primary=True) | Q(verified=True))
        try:
            email_address = qs.get(email__iexact=credentials["username"])
        except EmailAddress.DoesNotExist:
            return None
        else:
            user = email_address.user
            if user.check_password(credentials["password"]):
                return user
