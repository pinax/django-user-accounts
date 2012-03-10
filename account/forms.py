from django import forms
from django.utils.translation import ugettext_lazy as _

from django.contrib import auth


class SignupForm(forms.Form):
    pass


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
