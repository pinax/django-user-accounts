from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError
from django.template.loader import render_to_string
from django.utils import timezone

from django.contrib.sites.models import Site

from account import signals
from account.conf import settings
from account.utils import random_token


class EmailAddressManager(models.Manager):
    
    def add_email(self, user, email):
        try:
            email_address = self.create(user=user, email=email)
            email_address.send_confirmation()
            return email_address
        except IntegrityError:
            return None
    
    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except self.model.DoesNotExist:
            return None
    
    def get_users_for(self, email):
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [address.user for address in self.filter(verified=True, email=email)]


class EmailConfirmationManager(models.Manager):
    
    def confirm_email(self, confirmation_key):
        try:
            confirmation = self.get(confirmation_key=confirmation_key)
        except self.model.DoesNotExist:
            return None
        if not confirmation.key_expired():
            email_address = confirmation.email_address
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()
            signals.email_confirmed.send(sender=self.model, email_address=email_address)
            return email_address
    
    def send_confirmation(self, email_address):
        confirmation_key = random_token([email_address.email])
        current_site = Site.objects.get_current()
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        activate_url = u"%s://%s%s" % (
            protocol,
            unicode(current_site.domain),
            reverse("account_confirm_email", args=[confirmation_key])
        )
        ctx = {
            "user": email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "confirmation_key": confirmation_key,
        }
        subject = render_to_string("account/email/email_confirmation_subject.txt", ctx)
        subject = "".join(subject.splitlines()) # remove superfluous line breaks
        message = render_to_string("account/email/email_confirmation_message.txt", ctx)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email_address.email])
        confirmation = self.create(
            email_address=email_address,
            sent=timezone.now(),
            confirmation_key=confirmation_key
        )
        signals.email_confirmation_sent.send(
            sender=self.model,
            confirmation=confirmation,
        )
        return confirmation
    
    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmation.delete()
