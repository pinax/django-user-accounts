from account.models import EmailAddress, Account
from account.conf import settings

from django.contrib.auth import get_user_model


class SignupService():

    @staticmethod
    def signup(username, email, password, signup_code=None, *args, **kwargs):
        ss = SignupService()

        user = ss.__create_user(username, email, password, commit=False, **kwargs)

        # prevent User post_save signal from creating an Account instance
        # we want to handle that ourself.
        user._disable_account_creation = True
        user.save()

        if signup_code:
            signup_code.use(user)

        email_address = ss.__create_email_address(user, signup_code, **kwargs)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED and not email_address.verified:
            user.is_active = False
            user.save()

        ss.__create_account(user, **kwargs)

        return user, email_address

    def __create_account(self, user, **kwargs):
        return Account.create(request=None, user=user, create_email=False, **kwargs)

    def __create_user(self, username, email, password, commit=True, model=None, **kwargs):
        User = model
        if User is None:
            User = get_user_model()

        user = User(**kwargs)
        user.username = username
        user.email = email

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        if commit:
            user.save()

        return user

    def __create_email_address(cls, user, signup_code, **kwargs):
        kwargs.setdefault("primary", True)
        kwargs.setdefault("verified", False)

        if signup_code:
            kwargs["verified"] = signup_code.email and user.email == signup_code.email

        return EmailAddress.objects.add_email(user, user.email, **kwargs)


class SettingsService():
    @staticmethod
    def update_email(user, email, previous_email, confirm=None):
        """
        update a users email address.  email should be just the address
        while previous_email should be the EmailAddress object of the users
        existing primary email
        """
        if confirm is None:
            confirm = settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL
        # @@@ handle multiple emails per user
        if not previous_email:
            user.email = email
            EmailAddress.objects.add_email(user, email, primary=True, confirm=confirm)
            user.save()
        else:
            if email != previous_email.email:
                previous_email.change(email, confirm=confirm)
