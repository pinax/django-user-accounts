import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from django.contrib import auth
from django.contrib.auth.models import User

from account.conf import settings
from account.models import EmailAddress


alnum_re = re.compile(r"^\w+$")


class SignupForm(forms.Form):
    
    username = forms.CharField(
        label=_("Username"),
        max_length=30,
        widget=forms.TextInput(),
        required=True
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput(render_value=False)
    )
    email = forms.EmailField(widget=forms.TextInput(), required=True)
    code = forms.CharField(
        max_length=64,
        required=False,
        widget=forms.HiddenInput()
    )
    
    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(_("Usernames can only contain letters, numbers and underscores."))
        qs = User.objects.filter(username__iexact=self.cleaned_data["username"])
        if not qs.exists():
            return self.cleaned_data["username"]
        raise forms.ValidationError(_("This username is already taken. Please choose another."))
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        qs = EmailAddress.objects.filter(email__iexact=value)
        if not qs.exists() or not settings.ACCOUNT_EMAIL_UNIQUE:
            return value
        raise forms.ValidationError(_("A user is registered with this email address."))
    
    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data


class LoginForm(forms.Form):
    
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=False)
    )
    remember = forms.BooleanField(
        label = _("Remember Me"),
        required = False
    )
    user = None
    
    def clean(self):
        if self._errors:
            return
        user = auth.authenticate(**self.user_credentials())
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError(_("This account is inactive."))
        else:
            raise forms.ValidationError(self.authentication_fail_message)
        return self.cleaned_data
    
    def user_credentials(self):
        raise NotImplementedError("LoginForm must be subclassed to provide all user credentials")


class LoginUsernameForm(LoginForm):
    
    username = forms.CharField(label=_("Username"), max_length=30)
    authentication_fail_message = _("The username and/or password you specified are not correct.")
    
    def __init__(self, *args, **kwargs):
        super(LoginUsernameForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ["username", "password", "remember"]
    
    def user_credentials(self):
        return {
            "username": self.cleaned_data["username"],
            "password": self.cleaned_data["password"],
        }


class LoginEmailForm(LoginForm):
    
    email = forms.EmailField(label=_("Email"))
    authentication_fail_message = _("The email address and/or password you specified are not correct.")
    
    def __init__(self, *args, **kwargs):
        super(LoginEmailForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ["email", "password", "remember"]
    
    def user_credentials(self):
        return {
            "email": self.cleaned_data["email"],
            "password": self.cleaned_data["password"],
        }


class ChangePasswordForm(forms.Form):
    
    oldpassword = forms.CharField(
        label=_("Current Password"),
        widget=forms.PasswordInput(render_value=False)
    )
    password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label=_("New Password (again)"),
        widget=forms.PasswordInput(render_value=False)
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
    
    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(_("Please type your current password."))
        return self.cleaned_data["oldpassword"]
    
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]
    
    def save(self, user):
        user.set_password(self.cleaned_data["password1"])
        user.save()


class PasswordResetForm(forms.Form):
    
    email = forms.EmailField(label=_("Email"), required=True)
    
    def clean_email(self):
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED:
            if not EmailAddress.objects.filter(email__iexact=self.cleaned_data["email"], verified=True).count():
                raise forms.ValidationError(_("Email address not verified for any user account"))
        else:
            if not User.objects.filter(email__iexact=self.cleaned_data["email"]).count():
                raise forms.ValidationError(_("Email address not found for any user account"))
        return self.cleaned_data['email']


class PasswordResetTokenForm(forms.Form):
    
    password1 = forms.CharField(
        label = _("New Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = _("New Password (again)"),
        widget = forms.PasswordInput(render_value=False)
    )
    
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]


class SettingsForm(forms.Form):
    
    email = forms.EmailField(label=_("Email"), required=True)
    timezone = forms.ChoiceField(
        label=_("Timezone"),
        choices=settings.ACCOUNT_TIMEZONE_CHOICES,
        required=False
    )
    language = forms.ChoiceField(
        label=_("Language"),
        choices=settings.ACCOUNT_LANGUAGES,
        required=False
    )
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        qs = EmailAddress.objects.filter(email__iexact=value)
        if not qs.exists() or not settings.ACCOUNT_EMAIL_UNIQUE:
            return value
        raise forms.ValidationError(_("A user is registered with this email address."))
