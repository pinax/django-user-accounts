import datetime
import operator

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from account import signals
from account.managers import EmailAddressManager, EmailConfirmationManager
from account.signals import signup_code_sent, signup_code_used
from account.utils import random_token


class SignupCode(models.Model):
    
    class AlreadyExists(Exception):
        pass
    
    class InvalidCode(Exception):
        pass
    
    code = models.CharField(max_length=64, unique=True)
    max_uses = models.PositiveIntegerField(default=0)
    expiry = models.DateTimeField(null=True, blank=True)
    inviter = models.ForeignKey(User, null=True, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    sent = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    use_count = models.PositiveIntegerField(editable=False, default=0)
    
    def __unicode__(self):
        if self.email:
            return u"%s [%s]" % (self.email, self.code)
        else:
            return self.code
    
    @classmethod
    def exists(cls, code=None, email=None):
        checks = []
        if code:
            checks.append(Q(code=code))
        if email:
            checks.append(Q(email=code))
        return cls._default_manager.filter(reduce(operator.or_, checks)).exists()
    
    @classmethod
    def create(cls, **kwargs):
        email, code = kwargs.get("email"), kwargs.get("code")
        if kwargs.get("check_exists", True) and cls.exists(code=code, email=email):
            raise cls.AlreadyExists()
        expiry = timezone.now() + datetime.timedelta(hours=kwargs.get("expiry", 24))
        if not code:
            code = random_token([email]) if email else random_token()
        params = {
            "code": code,
            "max_uses": kwargs.get("max_uses", 0),
            "expiry": expiry,
            "inviter": kwargs.get("inviter"),
            "notes": kwargs.get("notes", "")
        }
        if email:
            params["email"] = email
        return cls(**params)
    
    @classmethod
    def check(cls, code):
        if code:
            try:
                signup_code = cls._default_manager.get(code=code)
            except cls.DoesNotExist:
                raise cls.InvalidCode()
            else:
                if signup_code.max_uses and signup_code.max_uses <= signup_code.use_count:
                    raise cls.InvalidCode()
                else:
                    if signup_code.expiry and timezone.now() > signup_code.expiry:
                        raise cls.InvalidCode()
                    else:
                        return signup_code
        else:
            return None
    
    def calculate_use_count(self):
        self.use_count = self.signupcoderesult_set.count()
        self.save()
    
    def use(self, user):
        """
        Add a SignupCode result attached to the given user.
        """
        result = SignupCodeResult()
        result.signup_code = self
        result.user = user
        result.save()
        signup_code_used.send(sender=result.__class__, signup_code_result=result)
    
    def send(self):
        current_site = Site.objects.get_current()
        domain = unicode(current_site.domain)
        ctx = {
            "signup_code": self,
            "domain": domain,
        }
        subject = render_to_string("account/email/invite_user_subject.txt", ctx)
        message = render_to_string("account/email/invite_user.txt", ctx)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])
        self.sent = timezone.now()
        self.save()
        signup_code_sent.send(sender=SignupCode, signup_code=self)


class SignupCodeResult(models.Model):
    
    signup_code = models.ForeignKey(SignupCode)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    
    def save(self, **kwargs):
        super(SignupCodeResult, self).save(**kwargs)
        self.signup_code.calculate_use_count()


class EmailAddress(models.Model):
    
    user = models.ForeignKey(User)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    primary = models.BooleanField(default=False)
    
    objects = EmailAddressManager()
    
    class Meta:
        verbose_name = _("email address")
        verbose_name_plural = _("email addresses")
        unique_together = [("user", "email")]
    
    def __unicode__(self):
        return u"%s (%s)" % (self.email, self.user)
    
    def set_as_primary(self, conditional=False):
        old_primary = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        self.user.email = self.email
        self.user.save()
        return True
    
    def send_confirmation(self):
        confirmation = EmailConfirmation.create(self)
        confirmation.send()
        return confirmation


class EmailConfirmation(models.Model):
    
    email_address = models.ForeignKey(EmailAddress)
    created = models.DateTimeField(default=timezone.now())
    sent = models.DateTimeField(null=True)
    key = models.CharField(max_length=64, unique=True)
    
    objects = EmailConfirmationManager()
    
    class Meta:
        verbose_name = _("email confirmation")
        verbose_name_plural = _("email confirmations")
    
    def __unicode__(self):
        return u"confirmation for %s" % self.email_address
    
    @classmethod
    def create(cls, email_address):
        key = random_token([email_address.email])
        return cls._default_manager.create(email_address=email_address, key=key)
    
    def key_expired(self):
        expiration_date = self.sent + datetime.timedelta(days=settings.ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS)
        return expiration_date <= timezone.now()
    key_expired.boolean = True
    
    def confirm(self):
        if not self.key_expired() and not self.email_address.verified:
            email_address = self.email_address
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()
            signals.email_confirmed.send(sender=self.__class__, email_address=email_address)
            return email_address
    
    def send(self):
        current_site = Site.objects.get_current()
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        activate_url = u"%s://%s%s" % (
            protocol,
            unicode(current_site.domain),
            reverse("account_confirm_email", args=[self.key])
        )
        ctx = {
            "user": self.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": self.key,
        }
        subject = render_to_string("account/email/email_confirmation_subject.txt", ctx)
        subject = "".join(subject.splitlines()) # remove superfluous line breaks
        message = render_to_string("account/email/email_confirmation_message.txt", ctx)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email_address.email])
        self.sent = timezone.now()
        self.save()
        signals.email_confirmation_sent.send(sender=self.__class__, confirmation=self)

class PasswordReset(models.Model):

    user = models.ForeignKey(User)
    temp_key = models.CharField(_("templ_key"), max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    reset = models.BooleanField(_('reset yet?'), default=False)

    def __unicode__(self):
        return "%s (key=%s, reset=%r)" %(self.user.username, self.temp_key, self.reset)

