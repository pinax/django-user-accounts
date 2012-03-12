import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from django.contrib import auth
from django.contrib.auth.models import User

from account.conf import settings
from account.models import SignupCode


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
        try:
            User.objects.get(username__iexact=self.cleaned_data["username"])
        except User.DoesNotExist:
            return self.cleaned_data["username"]
        raise forms.ValidationError(_("This username is already taken. Please choose another."))
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        try:
            User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            return value
        raise forms.ValidationError(_("A user is registered with this email address."))
    
    def clean_code(self):
        try:
            signup_code = SignupCode.check(self.cleaned_data.get("code"))
        except SignupCode.InvalidCode:
            if not settings.ACCOUNT_OPEN_SIGNUP:
                raise forms.ValidationError(_("Signup code is invalid."))
            else:
                return None
        else:
            if not settings.ACCOUNT_OPEN_SIGNUP and signup_code is None:
                raise forms.ValidationError(_("Code is required to signup."))
            return signup_code
    
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
