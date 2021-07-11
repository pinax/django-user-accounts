from django.db import models

from account.hooks import hookset


class EmailAddressManager(models.Manager):

    def add_email(self, user, email, **kwargs):
        confirm = kwargs.pop("confirm", False)
        email_address = self.create(user=user, email=email, **kwargs)
        if confirm and not email_address.verified:
            self.send_confirmation(email=email)
        return email_address

    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except self.model.DoesNotExist:
            return None

    def get_users_for(self, email):
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [address.user for address in self.filter(verified=True, email=email)]

    def send_confirmation(self, **kwargs):
        from account.models import EmailConfirmation
        confirmation = EmailConfirmation.create(kwargs['email'])
        confirmation.send(**kwargs)
        return confirmation


class EmailConfirmationManager(models.Manager):

    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmation.delete()


class UserEmailManager(models.Manager):
    """This manager needs to be inherited if you use the User
       model as the email model.
    """

    def send_confirmation(self, **kwargs):
        from account.models import EmailConfirmation
        confirmation = EmailConfirmation.create(self)
        confirmation.send(**kwargs)
        return confirmation
