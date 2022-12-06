import datetime
import functools
import operator
from urllib.parse import urlencode

from django import forms
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _

import pytz
from account import signals
from account.conf import settings
from account.fields import TimeZoneField
from account.hooks import hookset
from account.languages import DEFAULT_LANGUAGE
from account.managers import EmailAddressManager, EmailConfirmationManager
from account.signals import signup_code_sent, signup_code_used


class Account(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="account", verbose_name=_("user"), on_delete=models.CASCADE)
    timezone = TimeZoneField(_("timezone"))
    language = models.CharField(
        _("language"),
        max_length=10,
        choices=settings.ACCOUNT_LANGUAGES,
        default=DEFAULT_LANGUAGE,
    )

    @classmethod
    def for_request(cls, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            account = user.account
            if account:
                return account
        return AnonymousAccount(request)

    @classmethod
    def create(cls, request=None, **kwargs):
        create_email = kwargs.pop("create_email", True)
        confirm_email = kwargs.pop("confirm_email", None)
        account = cls(**kwargs)
        if "language" not in kwargs:
            if request is None:
                account.language = DEFAULT_LANGUAGE
            else:
                account.language = translation.get_language_from_request(request, check_path=True)
        account.save()
        if create_email and account.user.email:
            kwargs = {"primary": True}
            if confirm_email is not None:
                kwargs["confirm"] = confirm_email
            EmailAddress.objects.add_email(account.user, account.user.email, **kwargs)
        return account

    def __str__(self):
        return str(self.user)

    def now(self):
        """
        Returns a timezone aware datetime localized to the account's timezone.
        """
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone("UTC"))
        tz = settings.TIME_ZONE if not self.timezone else self.timezone
        return now.astimezone(pytz.timezone(tz))

    def localtime(self, value):
        """
        Given a datetime object as value convert it to the timezone of
        the account.
        """
        tz = settings.TIME_ZONE if not self.timezone else self.timezone
        if value.tzinfo is None:
            value = pytz.timezone(settings.TIME_ZONE).localize(value)
        return value.astimezone(pytz.timezone(tz))


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def user_post_save(sender, **kwargs):
    """
    After User.save is called we check to see if it was a created user. If so,
    we check if the User object wants account creation. If all passes we
    create an Account object.

    We only run on user creation to avoid having to check for existence on
    each call to User.save.
    """

    # Disable post_save during manage.py loaddata
    if kwargs.get("raw", False):
        return False

    user, created = kwargs["instance"], kwargs["created"]
    disabled = getattr(user, "_disable_account_creation", not settings.ACCOUNT_CREATE_ON_SAVE)
    if created and not disabled:
        Account.create(user=user)


class AnonymousAccount:

    def __init__(self, request=None):
        self.user = AnonymousUser()
        self.timezone = settings.TIME_ZONE
        if request is None:
            self.language = DEFAULT_LANGUAGE
        else:
            self.language = translation.get_language_from_request(request, check_path=True)

    def __str__(self):
        return "AnonymousAccount"


class SignupCode(models.Model):

    class AlreadyExists(Exception):
        pass

    class InvalidCode(Exception):
        pass

    code = models.CharField(_("code"), max_length=64, unique=True)
    max_uses = models.PositiveIntegerField(_("max uses"), default=0)
    expiry = models.DateTimeField(_("expiry"), null=True, blank=True)
    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, blank=True)
    notes = models.TextField(_("notes"), blank=True)
    sent = models.DateTimeField(_("sent"), null=True, blank=True)
    created = models.DateTimeField(_("created"), default=timezone.now, editable=False)
    use_count = models.PositiveIntegerField(_("use count"), editable=False, default=0)

    class Meta:
        verbose_name = _("signup code")
        verbose_name_plural = _("signup codes")

    def __str__(self):
        if self.email:
            return "{0} [{1}]".format(self.email, self.code)
        else:
            return self.code

    @classmethod
    def exists(cls, code=None, email=None):
        checks = []
        if code:
            checks.append(Q(code=code))
        if email:
            checks.append(Q(email=email))
        if not checks:
            return False
        return cls._default_manager.filter(functools.reduce(operator.or_, checks)).exists()

    @classmethod
    def create(cls, **kwargs):
        email, code = kwargs.get("email"), kwargs.get("code")
        if kwargs.get("check_exists", True) and cls.exists(code=code, email=email):
            raise cls.AlreadyExists()
        expiry = timezone.now() + datetime.timedelta(hours=kwargs.get("expiry", 24))
        if not code:
            code = hookset.generate_signup_code_token(email)
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
    def check_code(cls, code):
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

    def send(self, **kwargs):
        protocol = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
        current_site = kwargs["site"] if "site" in kwargs else Site.objects.get_current()
        if "signup_url" not in kwargs:
            signup_url = "{0}://{1}{2}?{3}".format(
                protocol,
                current_site.domain,
                reverse("account_signup"),
                urlencode({"code": self.code})
            )
        else:
            signup_url = kwargs["signup_url"]
        ctx = {
            "signup_code": self,
            "current_site": current_site,
            "signup_url": signup_url,
        }
        ctx.update(kwargs.get("extra_ctx", {}))
        hookset.send_invitation_email([self.email], ctx)
        self.sent = timezone.now()
        self.save()
        signup_code_sent.send(sender=SignupCode, signup_code=self)


class SignupCodeResult(models.Model):

    signup_code = models.ForeignKey(SignupCode, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def save(self, **kwargs):
        super(SignupCodeResult, self).save(**kwargs)
        self.signup_code.calculate_use_count()


class EmailAddress(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, unique=settings.ACCOUNT_EMAIL_UNIQUE)
    verified = models.BooleanField(_("verified"), default=False)
    primary = models.BooleanField(_("primary"), default=False)

    objects = EmailAddressManager()

    class Meta:
        verbose_name = _("email address")
        verbose_name_plural = _("email addresses")
        if not settings.ACCOUNT_EMAIL_UNIQUE:
            unique_together = [("user", "email")]

    def __str__(self):
        return "{0} ({1})".format(self.email, self.user)

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

    def send_confirmation(self, **kwargs):
        confirmation = EmailConfirmation.create(self)
        confirmation.send(**kwargs)
        return confirmation

    def change(self, new_email, confirm=True):
        """
        Given a new email address, change self and re-confirm.
        """
        with transaction.atomic():
            self.user.email = new_email
            self.user.save()
            self.email = new_email
            self.verified = False
            self.save()
            if confirm:
                self.send_confirmation()

    def validate_unique(self, exclude=None):
        super(EmailAddress, self).validate_unique(exclude=exclude)

        qs = EmailAddress.objects.filter(email__iexact=self.email)

        if qs.exists() and settings.ACCOUNT_EMAIL_UNIQUE:
            raise forms.ValidationError({
                "email": _("A user is registered with this email address."),
            })


class EmailConfirmation(models.Model):

    email_address = models.ForeignKey(EmailAddress, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    sent = models.DateTimeField(null=True)
    key = models.CharField(max_length=64, unique=True)

    objects = EmailConfirmationManager()

    class Meta:
        verbose_name = _("email confirmation")
        verbose_name_plural = _("email confirmations")

    def __str__(self):
        return "confirmation for {0}".format(self.email_address)

    @classmethod
    def create(cls, email_address):
        key = hookset.generate_email_confirmation_token(email_address.email)
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

    def send(self, **kwargs):
        current_site = kwargs["site"] if "site" in kwargs else Site.objects.get_current()
        protocol = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
        activate_url = "{0}://{1}{2}".format(
            protocol,
            current_site.domain,
            reverse(settings.ACCOUNT_EMAIL_CONFIRMATION_URL, args=[self.key])
        )
        ctx = {
            "email_address": self.email_address,
            "user": self.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": self.key,
        }
        hookset.send_confirmation_email([self.email_address.email], ctx)
        self.sent = timezone.now()
        self.save()
        signals.email_confirmation_sent.send(sender=self.__class__, confirmation=self)


class AccountDeletion(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(max_length=254)
    date_requested = models.DateTimeField(_("date requested"), default=timezone.now)
    date_expunged = models.DateTimeField(_("date expunged"), null=True, blank=True)

    class Meta:
        verbose_name = _("account deletion")
        verbose_name_plural = _("account deletions")

    @classmethod
    def expunge(cls, hours_ago=None):
        if hours_ago is None:
            hours_ago = settings.ACCOUNT_DELETION_EXPUNGE_HOURS
        before = timezone.now() - datetime.timedelta(hours=hours_ago)
        count = 0
        for account_deletion in cls.objects.filter(date_requested__lt=before, user__isnull=False):
            hookset.account_delete_expunge(account_deletion)
            account_deletion.date_expunged = timezone.now()
            account_deletion.save()
            count += 1
        return count

    @classmethod
    def mark(cls, user):
        account_deletion, created = cls.objects.get_or_create(user=user)
        account_deletion.email = user.email
        account_deletion.save()
        hookset.account_delete_mark(account_deletion)
        return account_deletion


class PasswordHistory(models.Model):
    """
    Contains single password history for user.
    """
    class Meta:
        verbose_name = _("password history")
        verbose_name_plural = _("password histories")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="password_history", on_delete=models.CASCADE)
    password = models.CharField(max_length=255)  # encrypted password
    timestamp = models.DateTimeField(default=timezone.now)  # password creation time


class PasswordExpiry(models.Model):
    """
    Holds the password expiration period for a single user.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="password_expiry", verbose_name=_("user"), on_delete=models.CASCADE)
    expiry = models.PositiveIntegerField(default=0)
